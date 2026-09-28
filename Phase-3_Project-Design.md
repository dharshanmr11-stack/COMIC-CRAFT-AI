# PHASE 3 – PROJECT DESIGN

## Project Title
ComicCraft – AI Comic Story Creator

## 1. System Architecture

User
↓
Frontend
↓
FastAPI Backend
↓
Gemini AI
↓
Story, Narration and Dialogue Generation
↓
Hugging Face AI
↓
Comic Image Generation
↓
Comic Panel Layout
↓
PDF Export
↓
Final Comic

## 2. System Modules

### Frontend Module
Provides the user interface for entering the story idea and viewing the generated comic.

### Backend Module
Handles user requests and controls the complete comic-generation workflow.

### AI Story Generation Module
Uses Gemini AI to generate the comic title, scenes, narration and dialogues.

### AI Image Generation Module
Uses Hugging Face AI to generate images for the comic panels.

### Comic Layout Module
Combines the generated images, narration and dialogues into comic panels.

### PDF Export Module
Converts the generated comic panels into a downloadable PDF.

## 3. Data Flow

1. User enters a story idea.
2. Frontend sends the request to the backend.
3. Backend sends the request to Gemini AI.
4. Gemini generates the comic story and dialogues.
5. Image generation creates panel images.
6. The layout module creates the comic panels.
7. The PDF module generates the final PDF.
8. The completed comic is displayed to the user.

## 4. User Interface Design

The application contains:

- Home page
- Story input section
- Generate Comic button
- Comic preview page
- Panel display
- Download PDF button
- Create Another Comic button

## 5. AI Integration Design

ComicCraft uses two AI services:

### Gemini AI
Used for:
- Story generation
- Scene generation
- Narration
- Character dialogues

### Hugging Face AI
Used for:
- Comic panel image generation

## 6. Input

User-provided comic story idea.

## 7. Processing

Story generation → Image generation → Panel creation → PDF generation.

## 8. Output

A complete 10-panel AI-generated comic with images, narration, dialogues and PDF export.

## 9. Conclusion

The project design defines the architecture, modules, data flow and AI integration required to build the ComicCraft application.