from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from pytube import YouTube
from django.conf import settings
import os
import assemblyai as aai
import openai
from yt_dlp import YoutubeDL
import logging

# Create your views here.
logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'blog.html')


@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)

        # get yt title
        title = yt_title(yt_link)

        # get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error': "Failed to get transcript"}, status=500)

        # use OpenAI to generate the blog
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error': "Failed to generate blog article"}, status=500)

        # save blog article to database

        # return blog article as a response
        return JsonResponse({'content': blog_content})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def yt_title(link):
    try:
        ydl_opts = {'quiet': True}  # To suppress output, remove if you need logging
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            title = info_dict.get('title', 'Unknown Title')
            return title
    except Exception as e:
        logger.error(f"Error retrieving title: {e}")
        return "Unknown Title"


def download_audio(link):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': 'C:\\Users\\HP\\PycharmProjects\\AI-blog\\ai_blog\\ffmpeg-2024-08-07-git-94165d1b79'
                               '-essentials_build\\bin',
            'outtmpl': os.path.join(settings.MEDIA_ROOT, '%(title)s.%(ext)s'),
        }
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            audio_file = ydl.prepare_filename(info_dict)
            audio_file = audio_file.replace('.webm', '.mp3')
            return audio_file
    except Exception as e:
        logger.error(f"Error in download_audio: {e}")
        return None


def get_transcription(link):
    audio_file = download_audio(link)
    aai.settings.api_key = "a1ddd66de0fe4072bfbe69ce06ae2def"

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)

    return transcript.text


def generate_blog_from_transcription(transcription):
    openai.api_key = "sk-proj" \
                     "-zGin5DVbgNNQogqBQ6LcFnzcVFFFWubdtZ54DCef26a9XynyF7WIcm5ImxT3BlbkFJYmowy" \
                     "N2KFnWVTnso5Jmqf0x5kjtcnciem46x0mMJ5Nksluar7HpwiG1-4A "

    prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, " \
             f"write it based on the transcript, but dont make it look like a youtube video, make it look like a " \
             f"proper blog article: \n\n{transcription}\n\nArticle: "

    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        # max_tokens=1000
    )

    generated_content = response.choices[0].text.strip()

    return generated_content
