# 🎬 LTX Video LoRA Training Workshop

Welcome to the LTX Video LoRA Training Workshop! This guide will walk you through the complete process of training a custom LoRA model for video generation using the LTX Video framework.

---

## 🔌 Part 0: Connect to Your VM Machine

Connect to your VM machine via SSH:

```bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null <username>@<ip_address>
```
use the password that you got in your e-mail

### Copy Files from VM to Your Local Machine

In order to copy files from the VM to your laptop (run from your local laptop):

```bash
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null <username>@<ip_address>:/remote/path/to/file /local/destination/
```

---

## 🚀 Part 1: Environment Setup


**Option 1: Clone the Repository (or use the one on your VM)**
> **Note:** You don't really need to run this step, because the VM machine already contains the code. You can skip directy to option 2

```bash
git clone https://github.com/Naomi-Ken-Korem/LTX-Video-Trainer.git
cd LTX-Video-Trainer
```

Then create a virtual environment and install dependencies:

```bash
uv venv
source .venv/bin/activate
uv sync
```

**Option 2: Use Existing Setup**

Instead of Option 1, you can simply activate the existing environment:

```bash
cd LTX-Video-Trainer
tmux
source .venv/bin/activate
```

---

## 📝 Part 2: Dataset Preparation

### Step 1: Generate Video Captions

Generate descriptive captions for your training videos using the built-in captioning tool:

```bash
python scripts/caption_videos.py <your_data_folder or simply use /canny_for_workshop>/target_videos \
    --output /canny_for_workshop/captions.json \
    --use-8bit \
    --instruction "Shortly describe the content of this video in two sentences, focus also on the colors of the videos"
```

**Parameters:**
- `--use-8bit`: Enables memory-efficient 8-bit quantization
- `--instruction`: Custom instruction for the captioning model (optional, uses default if omitted)

> **⚠️ Note:** Detailed instructions that result in longer captions will significantly increase preprocessing time.

### Step 2: Add Reference Paths to Dataset (after captions are ready)

Add reference video paths to your captions file:

```bash
python scripts/add_reference_paths.py /canny_for_workshop/captions.json
```

This script automatically adds a `reference_path` field to each entry in your dataset JSON.

---

## 🎥 Part 3: Video Encoding

### Understanding Resolution Selection

When selecting the resolution for VAE encoding, consider these factors:

1. **Don't exceed source resolution** - Prevents training the model on upscaled content
2. **Smaller = faster training** - But may lose important details
3. **Maintain aspect ratio** - Ensures captions remain relevant to the actual training content

### Resolution Requirements

- Width and height must be divisible by 32 (VAE spatial encoding requirement)
- Frames must follow the formula: `(N × 8) + 1` (VAE temporal encoding + 1 frame for image conditioning)

**Example:** For source videos at 1920×1080, we'll use **960×512×33 frames**

### Preprocess and Encode Videos

Before running the actual preprocess stage, it's recommended to test with a small subset of videos using the `--decode-videos` flag to ensure everything is configured correctly.

**Step 1:** Create a test subset of your captions:

To verify that the data is correct, you can run the same command with the `--decode-videos` flag to preview the actual training videos.
It is better to run this step on a small ammount of videos just to make sure everything goes fine. for that you can
cp /canny_for_workshop/captions.json /canny_for_workshop/short_test_captions.json
```

Then manually edit `short_test_captions.json` and remove most entries, keeping only 5-10 for testing.

**Step 2:** Run preprocessing with video decoding:

```bash
python scripts/preprocess_dataset.py /canny_for_workshop/short_test_captions.json \
    --resolution-buckets "960x512x33" \
    --caption-column "caption" \
    --video-column "media_path" \
    --model-source "LTXV_13B_097_DEV" \
    --reference-column "reference_path" \
    --decode-videos
```

**Step 3:** Review the decoded videos (placed in `/canny_for_workshop/.precomputed`) to verify both target videos and reference videos look correct.

### Preprocess and Encode Videos

Once you've verified everything looks good, run the full preprocessing: 

```bash
python scripts/preprocess_dataset.py /canny_for_workshop/captions.json \
    --resolution-buckets "960x512x33" \
    --caption-column "caption" \
    --video-column "media_path" \
    --model-source "LTXV_13B_097_DEV" \
    --reference-column "reference_path"
```

**What this does:**
- Loads videos from the dataset
- Resizes them to the specified resolution
- Encodes them into VAE latent space
- Saves the encodings for efficient training



---

## 🏋️ Part 4: Model Training

### Step 1: Configure Training Parameters

Edit the training configuration file:

```bash
micro configs/ltxv_13b_ic_lora.yaml
```

**Required parameters:**
- `data.preprocessed_data_root`: Set the path to your prepared dataset
- `validations.prompts`: Fill in validation prompts
- `validation.reference_videos`: Fill in path (you can use the same path from the training set)
- `wandb.enabled`: Set to `true` if you have a Weights & Biases account
- `hub.push_to_hub`: Set to `true` if you have a Hugging Face account
- `hub.hub_model_id`: Set your `account_name/ltxv_ic_lora`

**Optional parameters to adjust:**
- Learning rate
- Batch size
- Number of training steps
- LoRA rank and alpha (should be the same value)
- Save intervals 

### Step 2: Start Training

Launch the training process:

```bash
python scripts/train.py configs/ltxv_13b_ic_lora.yaml
```

Training outputs will be saved in the `outputs/` folder. Monitor your training progress on Weights & Biases dashboard.

---

## 🔄 Part 5: Checkpoint Conversion

### Convert Checkpoint for ComfyUI

After training completes, convert your checkpoint to ComfyUI format:

```bash
python scripts/convert_checkpoint.py \
    outputs/<your_folder>/checkpoints/<checkpoint_name> \
    --to-comfy
```

### Copy to ComfyUI Models Directory

```bash
cp <path_to_comfy_checkpoint> /ComfyUI/models/loras/
```

---

## 🎨 Part 6: Testing with ComfyUI

### Step 1: Launch ComfyUI

```bash
cd /ComfyUI
source .venv/bin/activate
python main.py --port 8188 --disable-cuda-malloc --listen 0.0.0.0
```

### Step 2: Access ComfyUI Interface

Open in your local browser:

```
http://<ip_address>:8188
```

### Step 3: Load and Run Workflow

1. **Load the workflow**: Download and import the workflow file from `https://github.com/Naomi-Ken-Korem/LTX-Video-Trainer/blob/workshop/canny_lora.json`
2. **Enable LoRA toggle**: Turn on the LoRA node
3. **Select your trained LoRA**: Choose your converted checkpoint from the dropdown
4. **Upload reference video**: Provide a video for conditioning
5. **Run the workflow**: Click "Run" to generate!

---

## 📊 Workshop Tips

### During Training:
- Monitor loss curves on wandb
- Check sample outputs generated during training
- Adjust learning rate if loss plateaus or diverges

### Resolution Selection:
| Source Resolution | Recommended Training Resolution |
|------------------|----------------------------------|
| 1920×1080        | 960×512×33 or 768×432×33        |
| 1280×720         | 640×352×33 or 512×288×33        |

---

## 🐛 Troubleshooting

### Out of Memory Errors
- Reduce `lora_rank` (and `alpha`) in config
- Use smaller resolution bucket
- Enable `--use-8bit` flag

### Poor Quality Results
- Train for more steps
- Increase LoRA rank
- Use higher resolution videos
- Improve caption quality

### ComfyUI Connection Issues
- Verify SSH port forwarding is active
- Check firewall settings
- Ensure ComfyUI is running on port 8188

---

## 📚 Additional Resources

- [LTX Video Documentation](https://github.com/Lightricks/LTX-Video)
- [LoRA Training Guide](../docs/training-guide.md)
- [Configuration Reference](../docs/configuration-reference.md)
- [Dataset Preparation Tips](../docs/dataset-preparation.md)

---

## 🎉 Workshop Complete!

Congratulations! You've successfully trained and tested a custom LoRA model for video generation. Experiment with different datasets, training parameters, and creative applications.

**Questions or Issues?** Feel free to reach out or open an issue on GitHub.

Happy training! 🚀
