# 評価処理の拡張方法

インスタンス管理者であれば、評価処理を拡張することができます。

`static/lib/user_defined.py` に次のようなPythonスクリプトを配置します。

```python
"""My custom metric."""

from .metric_base import CSVSubmissionMetric
from django.utils.translation import gettext_lazy as _


class MyMetric(CSVSubmissionMetric):
    name = 'my_metric'
    display_name = _('カスタム指標')

    def metric_fn(self, y_gt, y_pred, *args, **kwargs):
        return (y_gt*y_pred).sum()

metrics = {
        'my_metric': MyMetric,
        }
```

概略としては、評価処理クラスを定義し、`metrics`にディクショナリのキーに名前、値にクラスを格納するという内容です。


ステップバイステップでこのPythonスクリプトの内容を確認していきます。

まず、`static/lib/metric_base.py`に基底クラス `MetricBase` が定義されており、この派生クラスとして定義することになります。

```python
class MetricBase(abc.ABC):
    def __init__(self, public_lb_ratio: Real, *args, **kwargs):
        self.public_lb_ratio = public_lb_ratio

    @abstractmethod
    def __call__(
            self, gt_file: str, submitted_file: str, *args, **kwargs
            ) -> Tuple[Real, Real]:
        pass
```

評価処理インスタンスのコール `__call__` で正解ファイルパス、提出されたファイルパスが与えられるので、
戻り値としてパブリックリーダーボードのスコア、プライベートリーダーボードのスコアを返すようにします。

上記の `MyMetric` では、`MetricBase`にCSV読み込み `CSVReaderMixin` とパブリック・プライベートリーダーボード用にデータを分ける処理 `DataSplitterMixin` を追加した、次のようなクラス `CSVSubmissionMetric` の派生として定義しています。

```python
class CSVSubmissionMetric(
        MetricBase, CSVReaderMixin, DataSplitterMixin):
    @abstractmethod
    def metric_fn(self, y_gt: Array, y_pred: Array, *args, **kwargs):
        pass

    def __call__(
            self, gt_file: str, submitted_file: str,
            *args, **kwargs):
        y_gt = self.read_file(gt_file)
        y_pred = self.read_file(submitted_file)

        if len(y_pred) != len(y_gt):
            raise RuntimeError('Invalid sample size')

        y_pred_pub, y_gt_pub = self.split(
                y_gt, y_pred, self.public_lb_ratio)

        score_pub = self.metric_fn(y_gt_pub, y_pred_pub, *args, **kwargs)
        score_priv = self.metric_fn(y_gt, y_pred, *args, **kwargs)

        return score_pub, score_priv
```

`CSVSubmissionMetric` は `metric_fn` のみ実装すれば使用可能な評価処理クラスにできるようになっています。

そのため `MyMetric` は `metric_fn` のみを実装しています。
```python
    def metric_fn(self, y_gt, y_pred, *args, **kwargs):
        return (y_gt*y_pred).sum()
```

また、評価処理クラスの内部処理用の名前 `name` および表示用の名前 `display_name` をクラスのプロパティとして設定してください。 

```python
class MyMetric(CSVSubmissionMetric):
    name = 'my_metric'
    display_name = _('カスタム指標')
```

最後に、`metrics` にディクショナリの要素 (キーに名前、値にクラス)として登録するのを忘れないでください。

```python
metrics = {
        'my_metric': MyMetric,
        }
```
