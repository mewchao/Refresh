import tensorflow as tf
import pathlib

# 加载图像
data_dir = pathlib.Path(r"D:\garbage\garbage_classify_v2\garbage_classify_v2\train")

# 设置参数
batch_size = 32
img_height = 180
img_width = 180
epochs = 10


num_classes = 40
class_names = list(range(num_classes))
class_names = [str(i) for i in class_names]

# 训练数据集对象
train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    # 设置随机种子
    seed=123,
    # 统一调整为指定的大小
    batch_size=batch_size,
    image_size=(img_height, img_width),
    class_names=class_names,
)

# 验证数据集对象
val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="validation",
    # 设置随机种子
    seed=123,
    # 统一调整为指定的大小
    image_size=(img_height, img_width),
    batch_size=batch_size)


# 数据增强序列
data_augmentation = tf.keras.Sequential([
    # 随机翻转图像
    tf.keras.layers.experimental.preprocessing.RandomFlip('horizontal'),
    # 随机旋转图像  最大旋转角度为20%的范围
    tf.keras.layers.experimental.preprocessing.RandomRotation(0.2),
    # 随机缩放图像  最大缩放范围为20%的范围
    tf.keras.layers.experimental.preprocessing.RandomZoom(0.2),
])

train_ds = train_ds.map(lambda x, y: (data_augmentation(x), y))


# 标准化数据
normalization_layer = tf.keras.layers.Rescaling(1. / 255)

AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)


IMG_SIZE = 180

model = tf.keras.Sequential([
    tf.keras.layers.Rescaling(1. / 255),
    # tf.keras.layers.Conv2D 层是卷积层，用于处理二维图像数据。

    tf.keras.layers.Conv2D(32, 3, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.MaxPooling2D(),

    tf.keras.layers.Conv2D(32, 3, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.MaxPooling2D(),

    tf.keras.layers.Conv2D(32, 3, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    # tf.keras.layers.MaxPooling2D(),

    tf.keras.layers.Conv2D(32, 3, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    # tf.keras.layers.MaxPooling2D(),

    tf.keras.layers.Conv2D(32, 3, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    # tf.keras.layers.MaxPooling2D(),

    tf.keras.layers.Conv2D(32, 3, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    # tf.keras.layers.MaxPooling2D(),

    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Conv2D(32, 3, activation='relu'),
    # 创建一个最大池化层。它通常用于卷积神经网络中，以减少特征图的大小并提高模型的计算效率。
    # tf.keras.layers.MaxPooling2D(),

    # 在卷积层和全连接层之间使用。
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dropout(0.2),
    # 全连接层，用于处理一维向量数据
    tf.keras.layers.Dense(128, activation='relu'),
    # 输出大小为 num_classes   第四层也是Dense层，包含10个神经元，没有激活函数。这一层输出的结果可以看作是每个数字的"得分"，
    # 最终我们将根据这些得分选择最有可能的数字。
    tf.keras.layers.Dense(num_classes)
])

# 编译模型
model.compile(
    optimizer='adam',
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=['acc'])
#
# # 训练模型
# history = model.fit(
#     train_ds,
#     validation_data=val_ds,
#     epochs=10
# )

# 训练后看一下
# history.history.keys()
#
# plt.plot(history.epoch, history.history.get('loss'), label='loss')
# plt.plot(history.epoch, history.history.get('val_loss'), label='val_loss')
# plt.legend()
#
# plt.plot(history.epoch, history.history.get('acc'), label='acc')
# plt.plot(history.epoch, history.history.get('val_acc'), label='val_acc')
# plt.legend()
#
# # 保存模型
# model.save('my_model2')
