# -*- coding: UTF-8 -*-

from PIL import Image
from PIL import ImageColor
import os

def getIcon():

	# 提示 获取输入
	print '请按以下顺序依次输入所需参数：'
	print '原图片路径 生成图片保存路径 保存图片的文件夹名称'
	print '路径请勿以 / 结尾！'
	print '各个参数之间请以空格分开'

	imagePath = raw_input()
	paramters = str(imagePath).split()

	# paramters[1] = str(paramters[1])[:-2]
	print str(paramters[0])[-4:]


	if not os.path.isfile(paramters[0]):
		print '当前路径' + str(paramters[0]) +'不存在图片'
		return
		
	if not str(paramters[0])[-4:] == '.png':
		print '选取文件不是.png格式！'
		return

	icon = Image.open(str(paramters[0]).strip())

	width,height = icon.size
	if width != height:
		print 'icon size is invaild!'
		return
	
	sizes = [20,29,40,58,60,76,80,87,120,152,167,180]

	folderPath = getPath(str(paramters[-2]),str(paramters[-1]))
	if len(folderPath) == 0:
		return

	for size in sizes:
		space = size
		# print newWitdh
		quartersizedIcon = icon.resize((space,space))
		newImageName = str(space) + 'x' + str(space) + '.png'
		quartersizedIcon.save(os.path.join(folderPath,str(newImageName)))


def getPath(path,folderName):

	# 检测当前路径是否有重名文件夹
	lists = os.listdir(path)
	if str(folderName) in lists:
		print str(folderName) + ' exists!'
		return nil

	# 创建新的文件夹
	path =  os.path.join(path,str(folderName))
	# path =  os.path.join(os.getcwd(),'Desktop',str(folderName))
	# print path
	os.makedirs(path)
	
	return path

	
getIcon()
# print getPath('New Project11')