# Product Roadmap

## Version: 1.3 (Future)

### 🎯 Planned Features

---

## Feature: Slide Screenshots in Markdown Output

**Priority:** Medium  
**Complexity:** Low  
**Estimated Effort:** 2-3 hours  
**Status:** Planned

### Overview
Add option to include full slide screenshots (PNG renders) in the markdown output for PPTX files. This preserves visual design, layout, and formatting that may be lost in text extraction.

### Use Cases
- Presentations with complex visual layouts
- Slides with charts, diagrams, and infographics
- Design-heavy slides where aesthetics matter
- Fallback when text extraction is poor
- Reference material in Obsidian that needs visual context

### User Story
> "As a user converting PowerPoint presentations, I want to see a screenshot of each slide in my markdown notes, so that I can reference the original visual design and layout alongside the extracted text."

---

## Implementation Plan

### 1. UI Changes

**File:** `web/templates/index.html`
**Location:** Add to AI Settings section

```html
<div class="setting-item">
    <label class="toggle-switch">
        <input type="checkbox" id="slideScreenshotsToggle" checked>
        <span class="toggle-slider"></span>
    </label>
    <div class="setting-label">
        <strong>Include Slide Screenshots</strong>
        <small>Add visual renders of slides (PPTX only, increases file size)</small>
    </div>
</div>
```

**Estimated Time:** 10 minutes

---

### 2. Frontend JavaScript

**File:** `web/static/js/app.js`
**Function:** `handleFiles()`

Add to form data submission:
```javascript
const slideScreenshots = document.getElementById('slideScreenshotsToggle').checked;
formData.append('slide_screenshots', slideScreenshots);
```

**Estimated Time:** 5 minutes

---

### 3. Backend API Update

**File:** `src/web_app.py`
**Function:** `upload_files()`

Extract setting from request:
```python
slide_screenshots = request.form.get('slide_screenshots', 'true').lower() == 'true'

# Pass to job
jobs[job_id] = {
    # ...
    'slide_screenshots': slide_screenshots
}

# Pass to processing thread
thread = threading.Thread(
    target=process_file_job,
    args=(job_id, file_path, processor, ai_enhancement, ai_image_processing, slide_screenshots)
)
```

**Estimated Time:** 15 minutes

---

### 4. Slide Rendering Implementation

**File:** `src/converters/pptx_image_extractor.py`
**New Function:** `render_slide_screenshot()`

```python
def render_slide_screenshot(slide, slide_num: int, output_dir: Path, base_name: str) -> Optional[Path]:
    """Render a slide as a PNG screenshot.
    
    Args:
        slide: python-pptx Slide object
        slide_num: Slide number (1-indexed)
        output_dir: Directory to save screenshot
        base_name: Base filename
        
    Returns:
        Path to saved screenshot or None if failed
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Get slide dimensions (default PowerPoint: 10" x 7.5" at 96 DPI)
        slide_width = int(slide.presentation.slide_width / 914400 * 96)  # EMU to pixels
        slide_height = int(slide.presentation.slide_height / 914400 * 96)
        
        # Create blank canvas
        img = Image.new('RGB', (slide_width, slide_height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Render each shape on the slide
        for shape in slide.shapes:
            # Convert shape position/size from EMU to pixels
            left = int(shape.left / 914400 * 96)
            top = int(shape.top / 914400 * 96)
            width = int(shape.width / 914400 * 96)
            height = int(shape.height / 914400 * 96)
            
            # Render text shapes
            if hasattr(shape, "text_frame"):
                text = shape.text
                # Draw text box background
                draw.rectangle([left, top, left+width, top+height], 
                              fill='white', outline='gray')
                # Draw text (simplified)
                draw.text((left+5, top+5), text, fill='black')
            
            # Render image shapes
            elif hasattr(shape, "image"):
                try:
                    image_stream = io.BytesIO(shape.image.blob)
                    shape_img = Image.open(image_stream)
                    shape_img = shape_img.resize((width, height))
                    img.paste(shape_img, (left, top))
                except:
                    pass
        
        # Save screenshot
        screenshot_path = output_dir / f"{base_name}_slide_{slide_num:02d}.png"
        img.save(screenshot_path, 'PNG', optimize=True)
        
        return screenshot_path
        
    except Exception as e:
        logger.error(f"Failed to render slide {slide_num}: {e}")
        return None
```

**Alternative (Simpler):** Use `pptx-to-pdf` + `pdf2image` libraries:
```python
# Convert PPTX → PDF → Images
# Libraries: pdf2image, python-pptx
def render_slides_simple(pptx_path: Path, output_dir: Path) -> List[Path]:
    """Convert PPTX slides to PNG images via PDF."""
    from pdf2image import convert_from_path
    import tempfile
    
    # Convert PPTX to PDF (requires LibreOffice or similar)
    pdf_path = convert_pptx_to_pdf(pptx_path)
    
    # Convert PDF pages to images
    images = convert_from_path(pdf_path, dpi=150)
    
    screenshot_paths = []
    for i, image in enumerate(images, 1):
        img_path = output_dir / f"{pptx_path.stem}_slide_{i:02d}.png"
        image.save(img_path, 'PNG')
        screenshot_paths.append(img_path)
    
    return screenshot_paths
```

**Estimated Time:** 1-2 hours (depending on approach)

---

### 5. Integration into Converter

**File:** `src/converters/docling_converter.py`
**Function:** `convert()` and `_extract_images_pptx_fallback()`

For python-pptx fallback:
```python
def _extract_images_pptx_fallback(self, file_path: Path, include_screenshots: bool = False):
    """Extract images from PPTX, optionally including slide screenshots."""
    from pptx import Presentation
    
    prs = Presentation(file_path)
    images = []
    
    for slide_num, slide in enumerate(prs.slides, 1):
        # Render full slide screenshot if enabled
        if include_screenshots:
            screenshot_path = render_slide_screenshot(
                slide, slide_num, self.temp_dir, file_path.stem
            )
            if screenshot_path:
                img = Image.open(screenshot_path)
                images.append({
                    'image': img,
                    'path': str(screenshot_path),
                    'caption': f'Slide {slide_num}',
                    'slide_number': slide_num,
                    'is_slide_screenshot': True,  # Flag for special handling
                    'speaker_notes': get_speaker_notes(slide)
                })
        
        # Continue with regular image extraction
        # ... existing code ...
```

**Estimated Time:** 30 minutes

---

### 6. Markdown Output Integration

**File:** `src/obsidian_writer.py`
**Function:** `_build_markdown_body()`

Modify to include slide screenshots at the beginning of each slide section:

```python
def _build_markdown_body(self, content: DocumentContent, base_name: str, ai_analysis: Dict = None) -> str:
    # ... existing code ...
    
    # Group images by slide number
    slide_screenshots = [img for img in content.images if img.get('is_slide_screenshot')]
    regular_images = [img for img in content.images if not img.get('is_slide_screenshot')]
    
    # Add slide screenshots inline with slide text
    slides_text = content.get_text().split('\n## Slide ')
    
    for i, slide_section in enumerate(slides_text):
        if i == 0:
            body_parts.append(slide_section)  # Header before first slide
            continue
        
        slide_num = i
        body_parts.append(f"\n## Slide {slide_section}")
        
        # Add screenshot if available
        matching_screenshot = next(
            (img for img in slide_screenshots if img.get('slide_number') == slide_num),
            None
        )
        if matching_screenshot:
            img_path = self._save_image(matching_screenshot['image'], base_name, f"slide_{slide_num:02d}")
            rel_path = Path(img_path).relative_to(self.output_dir)
            body_parts.append(f"\n![[{rel_path}]]\n")
    
    # ... rest of existing code for regular images ...
```

**Estimated Time:** 45 minutes

---

### 7. Configuration & Documentation

**File:** `config/config.yaml`

Add option:
```yaml
processing:
  slide_screenshots:
    enabled: true  # Default
    dpi: 150  # Image quality (72-300)
    format: 'png'  # png or jpg
```

**File:** `WEB_UI_GUIDE.md`

Add section:
```markdown
### Slide Screenshots

When enabled, full slide renders will be included in the markdown output
for PowerPoint files. This is useful for:
- Preserving visual design and layout
- Viewing charts and diagrams
- Reference material alongside extracted text

**Note:** This increases output file size significantly (1-2MB per slide).
```

**Estimated Time:** 15 minutes

---

## Technical Considerations

### Dependencies
May need to add:
```python
# For simple approach (recommended)
pdf2image==1.16.3
python-pptx==0.6.23  # Already installed

# For advanced approach
Pillow==10.1.0  # Already installed
```

### Performance Impact
- **Time:** +2-3 seconds per slide for rendering
- **Storage:** +0.5-2MB per slide (PNG compressed)
- **Memory:** +50-100MB temporary during rendering

### File Size Examples
- **10-slide deck without screenshots:** 50KB markdown + 2MB images = 2.05MB
- **10-slide deck with screenshots:** 50KB markdown + 15MB images = 15.05MB
- **Recommendation:** Make it optional (default: OFF for file size)

---

## Testing Plan

### Unit Tests
1. Test slide rendering with various PPTX formats
2. Test with slides containing: text, images, charts, tables
3. Test error handling when rendering fails
4. Test file size limits with screenshots enabled

### Integration Tests
1. Upload PPTX with screenshots ON → Verify images in output
2. Upload PPTX with screenshots OFF → Verify no slide images
3. Test with both AI toggles and screenshot toggle
4. Verify Obsidian can display the embedded images

### User Acceptance
1. Compare markdown with/without screenshots
2. Verify visual quality is acceptable (150 DPI)
3. Check file sizes are reasonable
4. Confirm images render properly in Obsidian

---

## Rollout Plan

1. **Phase 1:** Implement basic rendering (simple approach with pdf2image)
2. **Phase 2:** Add UI toggle and pass setting through pipeline
3. **Phase 3:** Integrate into markdown output
4. **Phase 4:** Test with various PPTX files
5. **Phase 5:** Update documentation
6. **Phase 6:** Deploy and monitor file sizes

---

## Future Enhancements

- **Thumbnail view:** Generate smaller thumbnails (200px wide) instead of full-size
- **Selective screenshots:** Only screenshot slides with low text extraction quality
- **Format options:** JPEG instead of PNG for smaller files (50% size reduction)
- **Quality settings:** User-selectable DPI (72, 150, 300)
- **Smart detection:** Auto-enable for image-heavy slides, disable for text-heavy

---

## Success Metrics

- ✅ Feature toggle works in UI
- ✅ Screenshots render for 95%+ of slides
- ✅ File size increase < 100MB for typical deck
- ✅ No performance degradation (< 5 seconds per slide)
- ✅ Images display correctly in Obsidian
- ✅ Zero crashes or errors during rendering

---

**Last Updated:** 2025-11-11  
**Status:** Ready for implementation  
**Assigned To:** TBD  
**Estimated Completion:** 1 sprint (2 weeks)

