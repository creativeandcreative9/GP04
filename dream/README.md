# 雲上の月光工房 — 動きの知覚性を修正した60秒版

前回の軽量MP4を確認すると、主な雲塊は元の背景に固定されたままで、動く層は34%の薄い霞でした。カメラも最初の10秒で約0.5%のズーム変化、機械の画面位置で約13pxの移動に留まり、通常再生で動きが伝わりにくい設計でした。コードの周期性だけでは視聴上の合格にならないため、以下を変更しました。

## 修正内容

- 元の背景を画像生成で修復し、目立つ固定雲を除いた `assets/cloud-free-plate.png` を作成。月、浮島、工房の建築、照明と絵画調を維持しています。オリジナル背景ファイルも残しています。
- `assets/cloud-clusters.png` に3種類の立体的な雲塊を画像生成。薄い霞ではなく、約96%の不透明度を持つ本体を、窓の奥で独立して一定方向に流します。
- 雲塊は30px/秒、5秒で150px移動します。前景と別レイヤーで、カメラを固定しても雲は動きます。元の目立つ固定雲を取り除いたため、主な雲塊そのものが動きます。
- カメラは1.05〜1.15倍のズームと横±40px・縦±14pxの閉じた軌道。最初の5秒は1.10→1.125倍（約2.3%変化）、コーティング機械の画面上位置は約31px移動。60秒で位置・速度がつながります。
- 改善済みの機械・コンベヤ・クッキー素材、6秒の工場工程、60秒の空調・金属音は継続使用。

## リポジトリでの再生と保存内容

`output/dream-cloud-factory-preview-1080p.mp4` が承認済み完成プレビューです（60秒・1080p・音付き、約12.1MB）。`dream` フォルダで `python3 -m http.server 8000` を実行し、`http://localhost:8000/preview.html` を開くと再生できます。

高品質MP4は約48.8MBで通常のGitHubファイル上限には達しませんが、リポジトリを軽く保つため収録していません。Libraryの高品質版は保持し、必要なら下記手順で再生成できます。無音中間MP4、WAV、個別抽出フレーム、古い比較画像、キャッシュ、ZIPバックアップもGit対象外です。必要な画像生成素材は収録済みです。

## 成果物

- `output/dream-cloud-factory.mp4`: 再生成時に出力される高品質版（Git対象外）、60秒、1920×1080、30fps、H.264、AACステレオ。
- `output/dream-cloud-factory-preview-1080p.mp4`: チャット添付用の軽量版。60秒全部と音を含み、15MB未満。
- `output/contact-sheet.jpg`: 実際に書き出したMP4の0・5・10…55秒、終端、加工途中の画像一覧。
- `output/motion-check-5s.jpg`: 納品用の軽量MP4から抽出した0・5・10・15秒の比較画像。
- `output/verification.json` / `output/audio-verification.json`: 映像・音声の検証結果。

## 再生成

Python 3.11以上、FFmpeg / ffprobe（libx264）、DejaVu Sansが必要です。

```sh
sudo apt-get install ffmpeg fonts-dejavu-core python3-venv
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python render.py
python audio.py
ffmpeg -y -i output/dream-cloud-factory.mp4 -t 60 -map 0:v:0 -map 0:a:0 -c:v libx264 -preset medium -b:v 1500k -maxrate 1700k -bufsize 3000k -pix_fmt yuv420p -c:a aac -b:a 96k -ar 48000 -movflags +faststart output/dream-cloud-factory-preview-1080p.mp4
```

このREADMEのあるフォルダで実行してください。必要な生成画像は同梱済みで、画像生成APIの再呼び出しは不要です。画像生成自体は非決定的ですが、同梱素材からの動画生成は決定論的です。

```sh
python render.py --still 5
python render.py --verify
python audio.py --background-db -42 --process-db -28
python3 -m http.server 8000
```

`preview.html`で通常速度・音付きで再生できます。動画生成では1800フレームすべてを描画します。工場の180状態の透過前景をキャッシュし、動く雲・カメラと合成するため、約1GBのメモリを使用します。音色、工程時刻、音量設定は前回60秒版と同じです。

## 見た目の確認と限界

前回の納品済み軽量MP4から実フレームを取り出して問題を診断しました。今回も実際の高品質MP4と軽量MP4から5秒間隔の画像を抽出し、雲塊の位置、画角、機械の大きさの変化を比較します。数値と静止画だけを通常速度の視聴と同一視しません。この実行環境に動画を通常速度で視聴する機能はなく、実試聴もできません。この環境自身での通常速度視聴は未実施ですが、修正版はユーザーが確認し、完成版として承認済みです。

自動検証は、解像度・60秒・全1800フレームのデコード、3工程が全時刻画面内にあること、端の空白がないこと、雲が工場と独立して動くこと、ソースの0秒と60秒の一致、圧縮による細かなテクスチャ差と場面差を分けた継ぎ目の測定、カメラ補正後の製品変化、音声クリッピング・同期を対象にします。これらは知覚性の人による判定を代替しません。

2Dスプライトによる演出で、3D物理や液体シミュレーションではありません。空間構造のある元背景と画像生成素材の品質を保ちながら、雲レイヤーを分離しています。元のシンプル版と独立バックアップは維持しています。このリポジトリには完成版のソース・素材・軽量プレビューを保存します。高品質版とソースZIPはLibraryにも保存済みです。サイト公開やYouTube投稿は行っていません。

`python inspect_preview.py` は、軽量MP4の実フレームから機械の月飾り2点と雲の模様を相関追跡し、0→5秒の拡大率、パン、カメラを差し引いた雲の移動量を計測します。同じ実フレームから `motion-check-5s.jpg` を作成します。追加の検証結果は `output/preview-motion-measurements.json` にあります。
