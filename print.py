import os

# 要跳过的文件夹和文件
skip_folders = ["__pycache__", ".git"]
skip_files = [".gitignore", os.path.basename(__file__), "rbt_py.txt", "simple_biquote_peu.py"]

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 遍历目录下的所有文件和文件夹
for root, dirs, files in os.walk(current_dir):
    # 跳过指定的文件夹
    dirs[:] = [d for d in dirs if d not in skip_folders]
    for file in files:
        # 跳过指定的文件
        if file in skip_files:
            continue
        file_path = os.path.join(root, file)
        try:
            # 打印文件路径和文件名
            print(f"文件路径及文件名: {file_path}")
            # 读取文件内容
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # 打印文件内容
                print(content)
            # 打印分割线
            print("-" * 80)
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {e}")
            print("-" * 80)
