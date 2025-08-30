from flask import Flask, render_template, request, jsonify
import yt_dlp
import re


app = Flask(__name__)

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_basic_video_info(youtube_url):
    """Extract basic video info without captions"""
    try:
        print(f"Getting basic video info for: {youtube_url}")
        
        ydl_opts = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'extract_flat': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            
            if info:
                print(f"Successfully extracted basic info: {info.get('title', 'Unknown')}")
                return {
                    'title': info.get('title', 'Unknown Video'),
                    'duration': info.get('duration', 0),
                    'video_id': info.get('id', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'captions': []
                }
        
        return None
        
    except Exception as e:
        print(f"Error getting basic video info: {e}")
        return None

def parse_vtt_captions(vtt_content):
    """Parse VTT caption content into structured data"""
    captions = []
    lines = vtt_content.strip().split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for timestamp lines
        if '-->' in line:
            timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})', line)
            if timestamp_match:
                start_time = timestamp_match.group(1)
                end_time = timestamp_match.group(2)
                
                # Get caption text (next non-empty lines)
                caption_lines = []
                i += 1
                while i < len(lines) and lines[i].strip():
                    caption_text = lines[i].strip()
                    # Remove HTML tags and styling
                    caption_text = re.sub(r'<[^>]+>', '', caption_text)
                    if caption_text:
                        caption_lines.append(caption_text)
                    i += 1
                
                if caption_lines:
                    captions.append({
                        'start': convert_time_to_seconds(start_time),
                        'end': convert_time_to_seconds(end_time),
                        'text': ' '.join(caption_lines)
                    })
        
        i += 1
    
    return captions

def parse_srt_captions(srt_content):
    """Parse SRT caption content into structured data"""
    try:
        captions = []
        blocks = srt_content.strip().split('\n\n')
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                # Skip index line
                time_line = lines[1]
                text_lines = lines[2:]
                
                # Parse time format: 00:00:00,000 --> 00:00:04,000
                if ' --> ' in time_line:
                    start_str, end_str = time_line.split(' --> ')
                    start_time = srt_time_to_seconds(start_str.strip())
                    end_time = srt_time_to_seconds(end_str.strip())
                    text = ' '.join(text_lines).strip()
                    
                    if text:
                        captions.append({
                            'start': start_time,
                            'end': end_time,
                            'text': text
                        })
        
        return captions if captions else None
        
    except Exception as e:
        print(f"Error parsing SRT captions: {e}")
        return None

def parse_txt_captions(txt_content):
    """Parse plain text captions with timestamps"""
    try:
        captions = []
        lines = txt_content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to find timestamp patterns like [00:30] or (00:30) or 00:30 -
            # Pattern 1: [MM:SS] text
            match = re.match(r'\[(\d{1,2}):(\d{2})\]\s*(.+)', line)
            if match:
                minutes, seconds, text = match.groups()
                start_time = int(minutes) * 60 + int(seconds)
                captions.append({
                    'start': start_time,
                    'end': start_time + 3,  # Default 3 second duration
                    'text': text.strip()
                })
                continue
                
            # Pattern 2: (MM:SS) text
            match = re.match(r'\((\d{1,2}):(\d{2})\)\s*(.+)', line)
            if match:
                minutes, seconds, text = match.groups()
                start_time = int(minutes) * 60 + int(seconds)
                captions.append({
                    'start': start_time,
                    'end': start_time + 3,
                    'text': text.strip()
                })
                continue
                
            # Pattern 3: MM:SS - text
            match = re.match(r'(\d{1,2}):(\d{2})\s*[-–—]\s*(.+)', line)
            if match:
                minutes, seconds, text = match.groups()
                start_time = int(minutes) * 60 + int(seconds)
                captions.append({
                    'start': start_time,
                    'end': start_time + 3,
                    'text': text.strip()
                })
                continue
                
            # If no timestamp found, treat as sequential with 3-second intervals
            if captions:
                last_end = captions[-1]['end']
                captions.append({
                    'start': last_end,
                    'end': last_end + 3,
                    'text': line
                })
            else:
                captions.append({
                    'start': 0,
                    'end': 3,
                    'text': line
                })
        
        return captions if captions else None
        
    except Exception as e:
        print(f"Error parsing TXT captions: {e}")
        return None

def srt_time_to_seconds(time_str):
    """Convert SRT time format (HH:MM:SS,mmm) to seconds"""
    try:
        time_part, ms_part = time_str.split(',')
        h, m, s = map(int, time_part.split(':'))
        ms = int(ms_part)
        return h * 3600 + m * 60 + s + ms / 1000
    except Exception:
        return 0

def convert_time_to_seconds(time_str):
    """Convert time string (HH:MM:SS.mmm) to seconds"""
    try:
        time_parts = time_str.split(':')
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds_parts = time_parts[2].split('.')
        seconds = int(seconds_parts[0])
        milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
        
        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
        return total_seconds
    except Exception:
        return 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    data = request.get_json()
    youtube_url = data.get('url', '')
    
    if not youtube_url:
        return jsonify({'error': 'Please provide a YouTube URL'}), 400
    
    # Validate YouTube URL
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    print(f"Extracted video ID: {video_id}")
    
    # Try to extract basic video info only
    video_data = get_basic_video_info(youtube_url)
    
    # If yt-dlp fails, create a minimal response so video can still play
    if not video_data:
        print("yt-dlp failed, creating minimal video data")
        video_data = {
            'title': f'YouTube Video {video_id}',
            'duration': 0,
            'video_id': video_id,
            'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
            'captions': []
        }
    
    # No captions by default - users can upload their own
    video_data['captions'] = []
    
    return jsonify(video_data)

@app.route('/upload_captions', methods=['POST'])
def upload_captions():
    """Handle caption file upload"""
    try:
        if 'caption_file' not in request.files:
            return jsonify({'error': 'No caption file provided'}), 400
        
        file = request.files['caption_file']
        video_id = request.form.get('video_id', '')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not video_id:
            return jsonify({'error': 'No video ID provided'}), 400
        
        # Read file content
        content = file.read().decode('utf-8')
        filename = file.filename.lower()
        
        # Parse based on file extension
        if filename.endswith('.vtt'):
            captions = parse_vtt_captions(content)
        elif filename.endswith('.srt'):
            captions = parse_srt_captions(content)
        elif filename.endswith('.txt'):
            captions = parse_txt_captions(content)
        else:
            return jsonify({'error': 'Unsupported file format. Use VTT, SRT, or TXT files.'}), 400
        
        if not captions:
            return jsonify({'error': 'Could not parse caption file. Please check the format.'}), 400
        
        print(f"Successfully parsed {len(captions)} captions from uploaded file")
        
        return jsonify({
            'success': True,
            'captions': captions,
            'count': len(captions),
            'message': f'Successfully loaded {len(captions)} captions from {filename}'
        })
        
    except Exception as e:
        print(f"Error processing uploaded captions: {e}")
        return jsonify({'error': 'Failed to process caption file'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)