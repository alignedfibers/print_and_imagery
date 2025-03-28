def do_removebg(image):
    # Remove the background
    workingimg = remove(image)

    # Convert to RGBA if not already
    if workingimg.mode != "RGBA":
        workingimg = workingimg.convert("RGBA")

    # Create a white background
    white_bg = Image.new("RGBA", workingimg.size, (255, 255, 255, 255))
    white_bg.paste(workingimg, (0, 0), workingimg)

    # Convert back to RGB (removing alpha channel)
    final_image = white_bg.convert("RGB")
    # Save the processed image
    return final_image

def fade_edges_to_transparent(image)
    width, height = image.size
    # Create a mask for rounded corners and edge blending
    mask = Image.new("L", (width, height), 255)
    corner_radius = int(min(width, height) * corner_radius_ratio)
    # Generate rounded corner effect using an ellipse mask
    corner = Image.new("L", (corner_radius * 2, corner_radius * 2), 0)
    draw = ImageDraw.Draw(corner)
    draw.ellipse((0, 0, corner_radius * 2, corner_radius * 2), fill=255)
    # Apply corners to mask
    mask.paste(corner.crop((0, 0, corner_radius, corner_radius)), (0, 0))
    mask.paste(corner.crop((corner_radius, 0, corner_radius * 2, corner_radius)), (width - corner_radius, 0))
    mask.paste(corner.crop((0, corner_radius, corner_radius, corner_radius * 2)), (0, height - corner_radius))
    mask.paste(corner.crop((corner_radius, corner_radius, corner_radius * 2, corner_radius * 2)), (width - corner_radius, height - corner_radius))
    # Apply strong blending on edges
    for y in range(height):
        for x in range(width):
            dist_x = min(x, width - x)
            dist_y = min(y, height - y)
            edge_blend = min(dist_x, dist_y) / (width * 0.05)  # Blend within 5% of image width
            edge_blend = min(max(edge_blend, 0), 1)
            mask.putpixel((x, y), int(mask.getpixel((x, y)) * edge_blend))
    # Apply the rounded corners and edge blending mask
    blended_image = Image.new("RGBA", (width, height))
    blended_image.paste(image, (0, 0), mask)
    return blended_image

def upscale_image(image,scale=4):
    def check_cpu_optimizations():
        """ Check available CPU optimizations and enable them if supported. """
        optimizations = {
            "MKL": torch._C.has_mkl,
            "MKL-DNN": torch.backends.mkldnn.enabled,
            "OpenMP": torch.backends.openmp.is_available(),
            #"AVX": torch.has_avx,
            #"AVX2": torch.has_avx2,
            #"FMA": torch.has_fma,
        }
        
        do_info("\n🔍 CPU Optimizations Available:")
        for opt, available in optimizations.items():
            print(f"  {opt}: {'✅ Enabled' if available else '❌ Not Available'}")

        if not any(optimizations.values()):
            print("⚠ No CPU optimizations detected. Performance may be slow.")

    def load_model(model_path, scale):
        """ Load Real-ESRGAN model, forcing CPU execution """
        #This line creates an instance of the RRDBNet model, which is a ResNet-based super-resolution network used in Real-ESRGAN.
        """
            ### **📌 Breaking Down Each Parameter**
            | Parameter        | Value  | What It Does |
            |------------------|--------|-----------------------------------------------------------------------------------------|
            | `num_in_ch=3`    | `3`    | Number of input channels (3 for **RGB images**).                                        |
            | `num_out_ch=3`   | `3`    | Number of output channels (**also RGB**).                                               |
            | `num_feat=64`    | `64`   | Number of feature maps in the first convolution layer (controls model size).            |
            | `num_block=23`   | `23`   | Number of **Residual-in-Residual Dense Blocks (RRDB)** in the network (controls depth). |
            | `num_grow_ch=32` | `32`   | Growth factor for feature channels in dense connections (controls learning power).      |
            | `scale=scale`    | `4` (or user-defined) | Upscaling factor (e.g., **4x for 4x resolution boost**).                 |
        """    
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=scale)
        device = "cpu"
        
        upscaler = RealESRGANer(
            scale=scale,
            model_path=model_path,
            model=model,
            tile=200,  # Adjust if needed
            tile_pad=10,
            pre_pad=0,
            half=False,  # Disable FP16 (not needed for CPU)
            device=device
        )

        return upscaler
    
    """ Perform image upscaling on CPU """
    img = image
    model_path = "../models/RealESRGAN_x4plus.pth"

    if not os.path.exists(model_path):
        print(f"❌ Model file '{model_path}' not found. Download it from the official repo.")
        return

    check_cpu_optimizations()
    upscaler = load_model(model_path, scale)
    #Converts an image from OpenCV's default BGR color format to RGB.
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Enhance resolution
    returnimg, _extra = upscaler.enhance(img, outscale=scale)
    # Save output
    returnimg = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
    return returnimg