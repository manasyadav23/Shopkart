import urllib.request
import os

images = {
    'iphone15.jpg': 'Apple+iPhone+15+Pro',
    'samsung.jpg': 'Samsung+Galaxy+S24',
    'sony.jpg': 'Sony+WH-1000XM5',
    'nike.jpg': 'Nike+Air+Max+270',
    'levis.jpg': 'Levis+511',
    'instantpot.jpg': 'Instant+Pot+Duo',
    'alchemist.jpg': 'The+Alchemist',
    'dyson.jpg': 'Dyson+V15+Detect',
    'macbook.jpg': 'MacBook+Pro+16',
    'ipad.jpg': 'iPad+Pro',
    'watch.jpg': 'Apple+Watch+Ultra',
    'airpods.jpg': 'AirPods+Pro',
    'kindle.jpg': 'Kindle+Paperwhite',
    'echo.jpg': 'Echo+Dot',
    'ps5.jpg': 'PlayStation+5',
    'xbox.jpg': 'Xbox+Series+X',
    'switch.jpg': 'Nintendo+Switch',
    'dell.jpg': 'Dell+XPS+15',
    'asus.jpg': 'ASUS+ROG+Zephyrus',
    'bose.jpg': 'Bose+QuietComfort',
    'jbl.jpg': 'JBL+Charge+5',
    'gopro.jpg': 'GoPro+HERO12',
    'canon.jpg': 'Canon+EOS+R5',
    'nikon.jpg': 'Nikon+Z9',
    'lg.jpg': 'LG+C3+OLED',
    'coffee.jpg': 'Breville+Espresso',
    'blender.jpg': 'Vitamix+Blender',
    'sneakers.jpg': 'Adidas+Ultraboost',
    'jacket.jpg': 'North+Face+Jacket',
    'bag.jpg': 'Samsonite+Luggage',
    'perfume.jpg': 'Chanel+No.+5',
    'watch2.jpg': 'Rolex+Submariner'
}

base_url = "https://loremflickr.com/600/600/"
upload_dir = '/Users/rohit/Desktop/shopkart/static/uploads'

if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

for filename, keyword in images.items():
    url = base_url + keyword.replace('+', ',')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    filepath = os.path.join(upload_dir, filename)
    try:
        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Downloaded {filename} for {keyword}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")
