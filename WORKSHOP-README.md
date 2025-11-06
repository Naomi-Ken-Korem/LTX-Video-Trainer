email - 
remote connection
a small dataset of videos

in advnace - git, uv

git clone https://github.com/Naomi-Ken-Korem/LTX-Video-Trainer.git

cd LTX-Video-Trainer
uv venv
uv sync

run this command:
python scripts/caption_videos.py ../canny/target_videos --output ../canny/captions.json --use-8bit --instruction <"instruction for the video captioning mode, can be also empy and un with the defualt caption instruction in scripts/caption_vidoes.py"> --use-8bit

For example - 
python scripts/caption_videos.py ../canny/target_videos --output ../canny/captions.json --use-8bit --instruction "Shortly describe the content of this video in two sentences, focus also on the colors of the videos"
Note that in case of a instruction that result sin long caption, the captioning preprocess will take much longer time.



in parallel, let decide how precompute the vae encodings of the videos
Canny target video resolution is 1920x1080
Things to be aware of when we select the resoltion - 
1. not bigger than actual resltion - to make sure we are not teashing the model to output low res reuslts
2. smaller is faster training
3. close to original aspect ratio - in order to make sure that cption that run on full video will be relvant to the videos that are used in trainnig
Lets use 960x512x33 should split by 32 in width and hight due to vae encoding, and by 8 + 1 due to vae temporal incoding + 1 frame for image

Before actully running this code - 
The caption file should be ready, and you should add refernce_path into the caption.json file
python3 scripts/add_reference_paths.py ../canny/captions.json

Now you are ready to encode videos into the vae encoder latnet space
# Preprocess the dataset using the generated dataset.json
python scripts/preprocess_dataset.py ../canny/captions.json \
    --resolution-buckets "960x512x33" \
    --caption-column "caption" \
    --video-column "media_path" \
    --model-source "LTXV_13B_097_DEV" \
    --reference-column "reference_path"

While preparing the encodings, lets oreoare the config file

go to configs/ltxv_13b_ic_lora.yaml
And lets have a look - 

# Model configuration
model:
  model_source: "LTXV_13B_097_DEV" # Options: "LTXV_13B_097_DEV", "LTXV_2B_0.9.6_DEV", "LTXV_2B_0.9.5", "LTXV_2B_0.9.1", "LTXV_2B_0.9.0", or a HF repo/local path
  training_mode: "lora" # Options: "lora" or "full"
  load_checkpoint: null 

Note that you can load checkpoint to continue a lora training





