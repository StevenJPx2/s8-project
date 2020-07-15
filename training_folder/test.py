import streamlit as st
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
from PIL import Image

import tensorflow_datasets as tfds
from tensorflow_examples.models.pix2pix import pix2pix


AUTOTUNE = tf.data.experimental.AUTOTUNE
BUFFER_SIZE = 1000
BATCH_SIZE = 1
IMG_WIDTH = 256
IMG_HEIGHT = 256
OUTPUT_CHANNELS = 3
LAMBDA = 10
EPOCHS = 200
checkpoint_path = "../Outputs/checkpoints/train"


tfds.disable_progress_bar()

dataset, metadata = tfds.load(
    "cycle_gan/summer2winter_yosemite", with_info=True, as_supervised=True,
)


def random_jitter(image):
    # resizing to 286 x 286 x 3
    image = tf.image.resize(
        image, [286, 286], method=tf.image.ResizeMethod.NEAREST_NEIGHBOR
    )

    # randomly cropping to 256 x 256 x 3
    image = tf.image.random_crop(image, size=[IMG_HEIGHT, IMG_WIDTH, 3])

    # random mirroring
    image = tf.image.random_flip_left_right(image)

    return image


# normalize image to a range of [-1, 1]
def normalize(image):
    image = tf.cast(image, tf.float32)
    image = (image / 127.5) - 1
    return image


def preprocess_image_test(image, label):
    image = normalize(image)
    return image


def generate_images(model, test_input):
    prediction = model(test_input)

    display_list = np.array([test_input[0].numpy(), prediction[0].numpy()]) * 0.5 + 0.5
    title = ["Input Image", "Predicted Image"]

    st.image(display_list, caption=title, width=300)


def load_data():

    test_summer, test_winter = dataset["testA"], dataset["testB"]
    test_summer = (
        test_summer.map(preprocess_image_test, num_parallel_calls=AUTOTUNE)
        .cache()
        .shuffle(BUFFER_SIZE)
        .batch(1)
    )

    test_winter = (
        test_winter.map(preprocess_image_test, num_parallel_calls=AUTOTUNE)
        .cache()
        .shuffle(BUFFER_SIZE)
        .batch(1)
    )

    generator_g = pix2pix.unet_generator(OUTPUT_CHANNELS, norm_type="instancenorm")
    generator_f = pix2pix.unet_generator(OUTPUT_CHANNELS, norm_type="instancenorm")

    discriminator_x = pix2pix.discriminator(norm_type="instancenorm", target=False)
    discriminator_y = pix2pix.discriminator(norm_type="instancenorm", target=False)

    generator_g_optimizer = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)
    generator_f_optimizer = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)

    discriminator_x_optimizer = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)
    discriminator_y_optimizer = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)

    ckpt = tf.train.Checkpoint(
        generator_g=generator_g,
        generator_f=generator_f,
        discriminator_x=discriminator_x,
        discriminator_y=discriminator_y,
        generator_g_optimizer=generator_g_optimizer,
        generator_f_optimizer=generator_f_optimizer,
        discriminator_x_optimizer=discriminator_x_optimizer,
        discriminator_y_optimizer=discriminator_y_optimizer,
    )

    ckpt_manager = tf.train.CheckpointManager(ckpt, checkpoint_path, max_to_keep=5)

    # if a checkpoint exists, restore the latest checkpoint.
    if ckpt_manager.latest_checkpoint:
        ckpt.restore(ckpt_manager.latest_checkpoint)
        print("Latest checkpoint restored!!")

    return test_summer, test_winter, generator_g, generator_f


if __name__ == "__main__":

    """
    # Summer-to-Winter and Winter-to-Summer Image Generator

    ## Generate image from dataset
    """

    test_summer, test_winter, generator_g, generator_f = load_data()

    if st.button("Summer to Winter"):
        sample_summer = iter(test_summer.take(1))
        generate_images(generator_g, next(sample_summer))
    if st.button("Winter to Summer"):
        sample_winter = iter(test_winter.take(1))
        generate_images(generator_f, next(sample_winter))

    """
    ## Load your own image
    """

    uploaded_file = st.file_uploader("", type=["png", "jpg", "tif", "tiff"])
    if uploaded_file is not None:
        uploaded_file = (
            Image.open(uploaded_file).convert("RGB").resize((256, 256), Image.ANTIALIAS)
        )
        uploaded_file = tf.convert_to_tensor(
            tf.keras.preprocessing.image.img_to_array(uploaded_file)
        )
        uploaded_file = uploaded_file[:, :, :3]
        uploaded_file = normalize(uploaded_file[None, ...])

        if st.button("Winter style"):
            generate_images(generator_g, uploaded_file)
        if st.button("Summer style"):
            generate_images(generator_f, uploaded_file)
