# PyCaption - YouTube Video Captions Viewer

A modern Python web application that allows users to watch YouTube videos with interactive captions. The app automatically extracts captions from YouTube videos and provides an interactive viewing experience with synchronized caption highlighting and seeking functionality.

## Features

- **URL-based Video Loading**: Simply enter a YouTube URL to load any video
- **Automatic Caption Extraction**: Automatically fetches captions (both manual and auto-generated)
- **Interactive Captions**: Click on any caption to jump to that part of the video
- **Real-time Synchronization**: Captions highlight automatically as the video plays
- **Auto-scroll**: Caption panel automatically scrolls to keep the active caption visible
- **Responsive Design**: Modern, mobile-friendly interface
- **No Download Required**: Stream videos directly without downloading

## Installation

1. **Clone or navigate to the project directory:**

   ```bash
   cd /Users/sepehrgoodarzyar/Projects/PyCaption
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the Flask application:**

   ```bash
   python app.py
   ```

2. **Open your web browser and navigate to:**

   ```
   http://localhost:5000
   ```

3. **Use the application:**
   - Enter a YouTube URL in the input field
   - Click "Load Video" or press Enter
   - Wait for the video and captions to load
   - Watch the video with interactive captions:
     - Captions automatically highlight as the video plays
     - Click any caption to jump to that timestamp
     - The caption panel auto-scrolls to keep active captions visible

## Supported YouTube URL Formats

The application supports various YouTube URL formats:

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

## Technical Details

### Backend (Flask)

- **yt-dlp**: For extracting YouTube video information and captions
- **Flask**: Web framework for handling requests
- **VTT Parser**: Custom parser for WebVTT caption format

### Frontend

- **YouTube Iframe API**: For embedded video player
- **Vanilla JavaScript**: For caption synchronization and interaction
- **Modern CSS**: Responsive design with smooth animations
- **Real-time Updates**: 100ms intervals for caption synchronization

### Caption Features

- Supports both manual and auto-generated captions
- Prefers manual captions when available
- Falls back to auto-generated captions
- Supports multiple English variants (en, en-US)
- Real-time highlighting based on video timestamp
- Smooth auto-scrolling to active captions

## Dependencies

- **Flask 2.3.3**: Web framework
- **yt-dlp 2023.9.24**: YouTube video and caption extraction
- **requests 2.31.0**: HTTP requests for caption content
- **python-dotenv 1.0.0**: Environment variable management

## Browser Compatibility

The application works with all modern browsers that support:

- YouTube Iframe API
- ES6 JavaScript features
- CSS Grid and Flexbox
- Smooth scrolling

## Troubleshooting

### Common Issues:

1. **"Could not extract video information"**

   - Ensure the YouTube URL is valid and accessible
   - Some videos may have restrictions that prevent caption extraction

2. **"No captions available"**

   - The video may not have captions enabled
   - Try with a different video that has captions

3. **Video not loading**
   - Check your internet connection
   - Ensure the video is not private or region-restricted

### Development Mode:

The app runs in debug mode by default for development. For production deployment, set `debug=False` in `app.py`.

## License

This project is for educational and personal use. Please respect YouTube's Terms of Service when using this application.
