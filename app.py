import streamlit as st
import keepa

st.set_page_config(page_title="ミートくんのせどり君", page_icon="🐢", layout="wide")
st.title("🐢 ミートくん特製・グラフ付き調査くん")

def isbn13_to_10(isbn13):
    isbn13 = "".join(filter(str.isdigit, isbn13))
    if len(isbn13) != 13: return isbn13
    s = isbn13[3:12]
    check = 0
    for i in range(9):
        check += int(s[i]) * (10 - i)
    check = (11 - (check % 11)) % 11
    return s + (str(check) if check < 10 else 'X')

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    password = st.text_input("合言葉を入力してください", type="password")
    if st.button("ログイン"):
        if password == "kin29man":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("合言葉が違います！")
else:
    isbn = st.text_input("KDC20でISBNを読み込んでください", "")
    if st.button("調査開始！") and isbn:
        target = isbn13_to_10(isbn)
        api = keepa.Keepa('81v8iin6o078t2ioag0ik3r16avdtsh5m09eq0c1qc4gios7075t8emq7u2g806t')
        with st.spinner(f'調査中...'):
            try:
                results = api.query(target, domain='JP', stats=1)
                if len(results) > 0:
                    product = results[0]
                    st.success(f"お宝発見！ ID: {target}")
                    col1, col2, col3 = st.columns(3)
                    if 'stats' in product and product['stats']:
                        rank = product['stats']['current'][3]
                        col1.metric("Amazon順位", f"{rank}位")
                    csv_data = product.get('csv')
                    if csv_data and len(csv_data) > 1:
                        used_prices = [p for p in csv_data[1] if p > 0]
                        if used_prices:
                            col2.metric("現在の中古安値", f"{used_prices[-1]}円")
                            col3.metric("過去の最高値", f"{max(used_prices)}円")
                    st.write("---")
                    st.subheader("📈 Keepa グラフ")
                    graph_url = f"https://graph.keepa.com/pricehistory.png?domain=jp&asin={target}&used=1&rank=1"
                    st.image(graph_url, caption="価格・ランキング推移", use_container_width=True)
                    st.link_button("🌐 グラフが見えない場合はこちら（Keepa公式）", f"https://keepa.com/#!product/5-{target}")
                else:
                    st.error("商品が見つかりませんでした。")
            except Exception as e:
                st.error(f"システムエラー: {e}")
    if st.sidebar.button("ログアウト"):
        st.session_state.logged_in = False
        st.rerun()
