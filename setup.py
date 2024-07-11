from setuptools import setup, find_packages

setup(
    name='revkimi',  # 您的包名
    version='0.1.0',  # 版本号
    author='DrTang',  # 作者名
    description='A simple chatbot using the Kimi API',  # 简单描述
    long_description_content_type='text/markdown',  # 长描述的格式
    url='https://github.com/dd123-a/revkimi',  # 项目的URL
    packages=find_packages(),  # 包含的包
    install_requires=[
        'requests>=2.25.1',  # 依赖的requests库，您可以根据需要调整版本
        'typing-extensions',  # 如果您的Python版本低于3.7，需要这个库来支持Literal等
    ],
    classifiers=[
        # 项目分类，可以根据实际情况添加
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',  # 如果您的项目是MIT许可
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.7',  # 兼容的Python版本
    include_package_data=True,  # 包含包数据
    zip_safe=False
)
