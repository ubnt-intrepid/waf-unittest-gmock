# waf-unittest-gmock

Yet another Waf unittest framework for GoogleTest/GoogleMock users

[waf-unittest](https://github.com/tanakh/waf-unittest) っぽいやつ

  * Google Mock 1.7.0 を追加
  * テスト結果の出力を改善(予定)

## Usage

  * プロジェクト内の適当なディレクトリに展開
  * 展開したディレクトリの `src` をWaf側で読み込む
  
  ```python
  ...
  
  GMOCK_DIR = ['waf-unittest-gmock/src']

  def options(opt):
      opt.recurse(GMOCK_DIR)
      ...

  def configure(conf):
      conf.recurse(GMOCK_DIR)
      ...

  def build(bld):
      bld.recurse(GMOCK_DIR)
      ...

  ...
  ```

## License

Copyright (c) 2015 Yusuke Sasaki

This software is released under the MIT License, see [LICENSE](LICENSE).
