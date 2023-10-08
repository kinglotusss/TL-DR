from youtube_transcript_api import YouTubeTranscriptApi
def yt_transcript(videoID):
    trans = ""
    try:
        trans_dict = YouTubeTranscriptApi.get_transcript(videoID)
        for item in trans_dict:
            trans+= item['text'].lower()
        return(trans)
    except Exception as e:
        return str(e)


