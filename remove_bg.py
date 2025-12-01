from PIL import Image

def remove_white_background(input_path, output_path, threshold=240):
    """
    Removes white background from an image.
    Pixels lighter than the threshold will be made transparent.
    """
    try:
        img = Image.open(input_path)
        img = img.convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            # item is a tuple (R, G, B, A)
            if item[0] > threshold and item[1] > threshold and item[2] > threshold:
                newData.append((255, 255, 255, 0))  # Transparent
            else:
                newData.append(item)

        img.putdata(newData)
        img.save(output_path, "PNG")
        print(f"Successfully saved transparent logo to {output_path}")
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    input_file = "/home/matiasdev/crudfull/logonuevo.png"
    output_file = "/home/matiasdev/crudfull/logo_transparent_real.png"
    remove_white_background(input_file, output_file)
