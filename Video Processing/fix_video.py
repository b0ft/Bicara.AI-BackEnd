import moviepy.editor as mp
my_clip = mp.VideoFileClip("output.mp4")
my_clip.write_videofile("result.mp4")
