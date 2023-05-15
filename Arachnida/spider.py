from bs4 import BeautifulSoup
import argparse
import sys
import os
import requests

parser = argparse.ArgumentParser(description="The spider program allow you to extract all the images from a website, recursively, by providing a url as a parameter.")
parser.add_argument("url", help="The URL of the site you want to extract images from")
parser.add_argument("-r", help="recursively downloads the images in a URL received as a parameter", action="store_true")
parser.add_argument("-l", help="indicates the maximum depth level of the recursive download. If not indicated, it will be 5 (-r is required)", type=int, metavar="N")
parser.add_argument("-p", help="indicates the path where the downloaded files will be saved. If not specified, ./data/ will be used", default="data", metavar="PATH")
args = parser.parse_args()

if not args.url.startswith("http://") and not args.url.startswith("https://"):
	print("spider.py: error: url must begin with \"http(s)://\"")
	quit()
if args.l and not args.r:
	print("spider.py: error: argument -l: argument -r is required to use -l", file=sys.stderr)
	quit()
if args.r and not args.l:
	args.l = 5
if args.l and args.l <= 0:
	print("Invalid depth, resetting to 5")
	args.l = 5
#print(args.url)
html_page = requests.get(args.url).content
soup = BeautifulSoup(html_page, "html.parser")
images = []
for img in soup.findAll('img'):
    images.append(img.get('src'))

# if (not os.path.exists(args.p)):
os.system("rm -rf " + args.p)
os.system("mkdir " + args.p)
for img in images:
	if str(img).endswith('.jpg') or str(img).endswith('.jpeg') or str(img).endswith('.png') or str(img).endswith('.gif') or str(img).endswith('.bmp'):
		if not str(img).startswith("http"):
			# if str(img).startswith("//"):
			# 	img = str(img)[1:]
			img = args.url + str(img)
		img_data = requests.get(img).content
		print("img = ", img)
		with open(args.p + '/' + img.split('/')[-1], 'wb') as handler:
			handler.write(img_data)

def main():
	print("main")

if __name__ == "__main__":
	main()