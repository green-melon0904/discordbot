# Render 無料枠で Discord bot を24時間動かす手順

Render の無料 Web Service として bot を動かす。無料枠は15分アクセスが無いと
スリープするため、`keep_alive.py`（同梱の小さなWebサーバー）を立てて
UptimeRobot で定期 ping し、スリープを防ぐ構成。**クレジットカード不要。**

```
[UptimeRobot] --5分ごとにping--> [Render上のbot + keep_alive Webサーバー] <--> [Discord]
```

---

## 0. 前提（このリポジトリに用意済み）
- `keep_alive.py` … スリープ防止用Webサーバー（$PORTで待受、`OK`を返す）
- `bot.py` … `keep_alive()` 呼び出し済み
- `render.yaml` … Render用設定（free / start: `python bot.py`）
- `.python-version` … `3.12.8`
- `requirements.txt` … discord.py / python-dotenv
- `.gitignore` … `.env` 除外済み（**TOKENはGitHubに上がらない**）

---

## 1. GitHub に push

```bash
cd ~/discordbot
git init
git add .
git commit -m "Discord bot for Render deploy"
```

GitHub で **private リポジトリ**を作成し、表示される手順に従って push:

```bash
git remote add origin https://github.com/<あなたのID>/discordbot.git
git branch -M main
git push -u origin main
```

> `.env`（TOKEN）は `.gitignore` で除外されるので push されない。TOKEN は次の手順で Render に直接登録する。

---

## 2. Render に登録（クレカ不要）

1. https://render.com で **「Sign in with GitHub」** で登録
2. ダッシュボード → **New +** → **Blueprint**
3. さっきの `discordbot` リポジトリを選択 → `render.yaml` が自動検出される
4. デプロイ設定で **環境変数 `TOKEN`** の入力を求められるので、`.env` の中身（botトークン）を貼り付け
5. プランが **Free** になっていることを確認 → **Apply / Deploy**

> Blueprint がうまくいかない場合は、New + → **Web Service** → リポジトリ選択 →
> Build: `pip install -r requirements.txt` / Start: `python bot.py` /
> Plan: Free を手動設定し、Environment に `TOKEN` を追加でもOK。

---

## 3. デプロイ確認

- Render の **Logs** に `ログインしました` が出れば成功
- 発行されたURL（例 `https://discordbot-xxxx.onrender.com`）をブラウザで開き **`OK`** が表示されればWebサーバーもOK
- Discord 上で bot がオンラインになり、`/neko` などスラッシュコマンドが応答するか確認

---

## 4. スリープ防止（UptimeRobot）

無料・クレカ不要でスリープを防ぐ:

1. https://uptimerobot.com に無料登録
2. **Add New Monitor**
   - Monitor Type: **HTTP(s)**
   - URL: Render の URL（`https://discordbot-xxxx.onrender.com`）
   - Monitoring Interval: **5 minutes**
3. 保存 → 5分おきにアクセスが入り、15分スリープを防げる

これで24時間稼働。20分ほど放置してもbotがオンラインのままなら成功。

---

## 5. 更新のしかた

コードを直したら:

```bash
git add . && git commit -m "update" && git push
```

Render が push を検知して**自動で再デプロイ**する。

---

## 補足・注意
- **Discord Developer Portal**: `bot.py` は `intents.members = True` を使うので、
  Bot 設定の **「Server Members Intent」が ON** であること（ローカルでログインできているので有効済みのはず）。
  Message Content Intent は未使用なので不要（起動時の警告は無視可）。
- **無料枠の制限**: 月750時間（≒1サービス常時稼働分）。bot は1つだけ常駐させる想定。
- TOKEN を絶対に GitHub に上げない（`.env` は `.gitignore` 済み。Render の環境変数で管理）。
- 万一トークンを公開してしまったら、Developer Portal で **Reset Token** し、`.env` と Render 両方を更新する。
