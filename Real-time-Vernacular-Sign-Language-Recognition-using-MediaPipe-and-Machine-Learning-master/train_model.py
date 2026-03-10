"""
快速训练手语识别模型
基于 ASL (美国手语) 数据集
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import joblib
import os

def train_asl_model():
    print("=" * 50)
    print("手语识别模型训练")
    print("=" * 50)

    # 加载数据
    data_path = os.path.join(os.path.dirname(__file__), 'Preprocessed-Data', 'american.csv')
    print(f"\n1. 加载数据: {data_path}")

    df = pd.read_csv(data_path)
    df.columns = [i for i in range(df.shape[1])]
    df = df.rename(columns={42: 'Output'})

    print(f"   原始数据: {df.shape[0]} 条记录")

    # 清理空值
    all_null_values = df[df.iloc[:, 0] == 0]
    df.drop(all_null_values.index, inplace=True)
    print(f"   清理后: {df.shape[0]} 条记录")

    # 准备特征和标签
    X = df.iloc[:, :-1]
    Y = df.iloc[:, -1]

    print(f"   特征数: {X.shape[1]}")
    print(f"   类别数: {Y.nunique()} ({', '.join(sorted(Y.unique()))})")

    # 分割数据
    print("\n2. 分割数据 (80% 训练, 20% 测试)")
    x_train, x_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.2, random_state=0
    )

    # 训练模型
    print("\n3. 训练 SVM 模型...")
    print("   参数: C=100, gamma=0.1, kernel='rbf'")

    svm = SVC(C=100, gamma=0.1, kernel='rbf')
    svm.fit(x_train, y_train)

    # 评估
    train_score = svm.score(x_train, y_train)
    y_pred = svm.predict(x_test)
    test_score = accuracy_score(y_test, y_pred)

    print(f"\n4. 模型评估:")
    print(f"   训练准确率: {train_score * 100:.2f}%")
    print(f"   测试准确率: {test_score * 100:.2f}%")

    # 保存模型
    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    joblib.dump(svm, model_path)
    print(f"\n5. 模型已保存: {model_path}")

    print("\n" + "=" * 50)
    print("✅ 训练完成! 现在可以运行 hand_detection_webcam.py")
    print("=" * 50)

    return svm

if __name__ == "__main__":
    train_asl_model()
