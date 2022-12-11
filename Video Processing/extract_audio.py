import moviepy.editor as mp
my_clip = mp.VideoFileClip("video.mp4")
my_clip.audio.write_audiofile("audio.mp3")



