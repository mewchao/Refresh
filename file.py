import os

path = r"D:\garbage\garbage_classify_v2\garbage_classify_v2\train\39"

# 获取文件夹中的所有文件并按字母顺序排序
files = sorted(os.listdir(path))

# 遍历每个文件并执行所需的操作
for file in files:
    # 这里可以加入任何你需要执行的操作
    if file.endswith(".txt"):
        file_path = os.path.join(path, file)

        # 判断文件是否存在
        if os.path.exists(file_path):
            # 删除文件
            os.remove(file_path)
            print(f"文件 {file_path} 已成功删除！")
        else:
            print(f"文件 {file_path} 不存在！")
        # with open(file_path, 'rb') as f:
        # content = f.read()
        # print(type(content))
        # f.seek(-2, 2)
        # if f.read() == b'26':
        # print(file)
