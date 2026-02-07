from downBili import download_video
from exAudio import flv_mp3

av = input("请输入av号：")
filename = download_video(av)
flv_mp3(filename)
print("音频提取完成！", f"audio/conv/{filename}.mp3")
