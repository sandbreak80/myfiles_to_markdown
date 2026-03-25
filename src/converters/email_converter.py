"""Email converter for EML, MSG, and MBOX formats."""

from pathlib import Path
from typing import Optional, List, Dict
import email
from email import policy
from email.parser import BytesParser
import mailbox
from loguru import logger
from datetime import datetime

from converters.base_converter import DocumentContent


class EmailConverter:
    """Convert email files (EML, MSG, MBOX) to markdown."""
    
    def __init__(self, config: dict):
        """Initialize email converter.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.supported_formats = {'.eml', '.msg', '.mbox'}
    
    def can_convert(self, file_path: Path) -> bool:
        """Check if file can be converted.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if supported format
        """
        return file_path.suffix.lower() in self.supported_formats
    
    def convert(self, file_path: Path) -> DocumentContent:
        """Convert email file to DocumentContent.
        
        Args:
            file_path: Path to email file
            
        Returns:
            DocumentContent object
        """
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.eml':
            return self._convert_eml(file_path)
        elif file_ext == '.msg':
            return self._convert_msg(file_path)
        elif file_ext == '.mbox':
            return self._convert_mbox(file_path)
        else:
            logger.error(f"Unsupported email format: {file_ext}")
            content = DocumentContent()
            content.title = file_path.stem
            content.text = f"# {file_path.stem}\n\nUnsupported email format: {file_ext}"
            return content
    
    def _convert_eml(self, file_path: Path) -> DocumentContent:
        """Convert EML file to DocumentContent.
        
        Args:
            file_path: Path to EML file
            
        Returns:
            DocumentContent object
        """
        logger.info(f"Converting EML: {file_path.name}")
        
        try:
            # Parse EML file
            with open(file_path, 'rb') as f:
                msg = BytesParser(policy=policy.default).parse(f)
            
            # Extract email data
            email_data = self._extract_email_data(msg)
            
            # Build markdown content
            content_parts = []
            
            # Title (ensure it's a string)
            subject = str(email_data['subject']) if email_data['subject'] else 'No Subject'
            content_parts.append(f"# {subject}\n")
            
            # Email metadata
            content_parts.append("## Email Details\n")
            content_parts.append(f"**From:** {email_data['from']}")
            content_parts.append(f"**To:** {email_data['to']}")
            if email_data['cc']:
                content_parts.append(f"**CC:** {email_data['cc']}")
            content_parts.append(f"**Date:** {email_data['date']}")
            if email_data['reply_to']:
                content_parts.append(f"**Reply-To:** {email_data['reply_to']}")
            content_parts.append("")
            
            # Email body
            content_parts.append("## Message\n")
            content_parts.append(email_data['body'])
            
            # Attachments
            if email_data['attachments']:
                content_parts.append("\n## Attachments\n")
                for att in email_data['attachments']:
                    content_parts.append(f"- **{att['filename']}** ({att['size']} bytes, {att['content_type']})")
            
            full_text = "\n".join(content_parts)
            
            # Create DocumentContent
            content = DocumentContent()
            content.title = subject
            content.text = full_text
            content.metadata = {
                'from': str(email_data['from']),
                'to': str(email_data['to']),
                'cc': str(email_data['cc']),
                'date': str(email_data['date']),
                'subject': str(subject),
                'attachment_count': len(email_data['attachments']),
                'has_html': email_data['has_html'],
                'file_size': file_path.stat().st_size
            }
            
            logger.success(f"EML converted: {len(email_data['attachments'])} attachments")
            return content
            
        except Exception as e:
            logger.error(f"Failed to convert EML {file_path.name}: {e}")
            content = DocumentContent()
            content.title = file_path.stem
            content.text = f"# {file_path.stem}\n\nError converting EML: {str(e)}"
            content.metadata = {'error': str(e)}
            return content
    
    def _convert_msg(self, file_path: Path) -> DocumentContent:
        """Convert MSG (Outlook) file to DocumentContent.
        
        Args:
            file_path: Path to MSG file
            
        Returns:
            DocumentContent object
        """
        logger.info(f"Converting MSG: {file_path.name}")
        
        try:
            # Try to import extract_msg
            try:
                import extract_msg
            except ImportError:
                logger.warning("extract-msg not installed, cannot convert MSG files")
                content = DocumentContent()
                content.title = file_path.stem
                content.text = f"# {file_path.stem}\n\n**Error:** extract-msg library not installed.\n\nInstall with: pip install extract-msg"
                return content
            
            # Open MSG file
            msg = extract_msg.Message(str(file_path))
            
            # Extract data
            subject = msg.subject or 'No Subject'
            from_addr = msg.sender or 'Unknown'
            to_addr = msg.to or 'Unknown'
            cc_addr = msg.cc or ''
            date = msg.date or 'Unknown'
            body = msg.body or '(No message body)'
            
            # Build markdown
            content_parts = []
            content_parts.append(f"# {subject}\n")
            content_parts.append("## Email Details\n")
            content_parts.append(f"**From:** {from_addr}")
            content_parts.append(f"**To:** {to_addr}")
            if cc_addr:
                content_parts.append(f"**CC:** {cc_addr}")
            content_parts.append(f"**Date:** {date}")
            content_parts.append("")
            content_parts.append("## Message\n")
            content_parts.append(body)
            
            # Attachments
            attachments = msg.attachments
            if attachments:
                content_parts.append("\n## Attachments\n")
                for att in attachments:
                    att_name = getattr(att, 'longFilename', None) or getattr(att, 'shortFilename', 'Unknown')
                    content_parts.append(f"- **{att_name}**")
            
            msg.close()
            
            full_text = "\n".join(content_parts)
            
            # Create DocumentContent
            content = DocumentContent()
            content.title = subject
            content.text = full_text
            content.metadata = {
                'from': str(from_addr),
                'to': str(to_addr),
                'cc': str(cc_addr),
                'date': str(date),
                'subject': str(subject),
                'attachment_count': len(attachments) if attachments else 0,
                'file_size': file_path.stat().st_size
            }
            
            logger.success(f"MSG converted successfully")
            return content
            
        except Exception as e:
            logger.error(f"Failed to convert MSG {file_path.name}: {e}")
            content = DocumentContent()
            content.title = file_path.stem
            content.text = f"# {file_path.stem}\n\nError converting MSG: {str(e)}"
            content.metadata = {'error': str(e)}
            return content
    
    def _convert_mbox(self, file_path: Path) -> DocumentContent:
        """Convert MBOX archive to DocumentContent.
        
        Args:
            file_path: Path to MBOX file
            
        Returns:
            DocumentContent object with multiple emails
        """
        logger.info(f"Converting MBOX: {file_path.name}")
        
        try:
            # Open MBOX file
            mbox = mailbox.mbox(str(file_path))
            
            # Build markdown for all emails
            content_parts = []
            content_parts.append(f"# Email Archive: {file_path.stem}\n")
            content_parts.append(f"**Total Messages:** {len(mbox)}\n")
            content_parts.append("---\n")
            
            # Process each email
            for i, message in enumerate(mbox, 1):
                email_data = self._extract_email_data(message)
                subject = email_data['subject'] or 'No Subject'
                
                content_parts.append(f"\n## Message {i}: {subject}\n")
                content_parts.append(f"**From:** {email_data['from']}")
                content_parts.append(f"**To:** {email_data['to']}")
                content_parts.append(f"**Date:** {email_data['date']}")
                content_parts.append("")
                
                # Add body (truncate if too long)
                body = email_data['body']
                if len(body) > 1000:
                    body = body[:1000] + "\n\n*(message truncated)*"
                content_parts.append(body)
                
                if email_data['attachments']:
                    content_parts.append(f"\n**Attachments:** {len(email_data['attachments'])}")
                
                content_parts.append("\n---\n")
            
            full_text = "\n".join(content_parts)
            
            # Create DocumentContent
            content = DocumentContent()
            content.title = f"Email Archive: {file_path.stem}"
            content.text = full_text
            content.metadata = {
                'message_count': len(mbox),
                'file_size': file_path.stat().st_size
            }
            
            logger.success(f"MBOX converted: {len(mbox)} messages")
            return content
            
        except Exception as e:
            logger.error(f"Failed to convert MBOX {file_path.name}: {e}")
            content = DocumentContent()
            content.title = file_path.stem
            content.text = f"# {file_path.stem}\n\nError converting MBOX: {str(e)}"
            content.metadata = {'error': str(e)}
            return content
    
    def _extract_email_data(self, msg) -> Dict:
        """Extract data from email message.
        
        Args:
            msg: Email message object
            
        Returns:
            Dictionary with email data
        """
        # Extract headers (ensure all are strings)
        subject = str(msg.get('subject', 'No Subject'))
        from_addr = str(msg.get('from', 'Unknown'))
        to_addr = str(msg.get('to', 'Unknown'))
        cc_addr = str(msg.get('cc', ''))
        reply_to = str(msg.get('reply-to', ''))
        date = str(msg.get('date', 'Unknown'))
        
        # Extract body
        body = ''
        has_html = False
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break  # Prefer plain text
                    except:
                        pass
                elif content_type == "text/html" and not body:
                    has_html = True
                    try:
                        # Simple HTML stripping
                        html_body = part.get_payload(decode=True).decode(errors='ignore')
                        # Basic HTML tag removal
                        import re
                        body = re.sub('<[^<]+?>', '', html_body)
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode(errors='ignore')
            except:
                body = str(msg.get_payload())
        
        # Extract attachments
        attachments = []
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            'filename': filename,
                            'content_type': part.get_content_type(),
                            'size': len(part.get_payload(decode=True)) if part.get_payload() else 0
                        })
        
        return {
            'subject': subject,
            'from': from_addr,
            'to': to_addr,
            'cc': cc_addr,
            'reply_to': reply_to,
            'date': date,
            'body': body.strip() if body else '(No message body)',
            'attachments': attachments,
            'has_html': has_html
        }

