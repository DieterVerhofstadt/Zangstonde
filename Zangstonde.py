import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Zangstonde", page_icon="🎶", layout="centered")


@st.cache_resource
def db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def norm(name: str) -> str:
    return " ".join(name.split()).casefold()


# ---------- wie ben je? ----------
name_raw = st.query_params.get("naam", "")
if not norm(name_raw):
    st.title("Zangstonde 🎶")
    with st.form("login"):
        n = st.text_input("Wie ben je? (voornaam)")
        if st.form_submit_button("Verder") and norm(n):
            st.query_params["naam"] = " ".join(n.split())
            st.rerun()
    st.stop()

me = norm(name_raw)
shown = me.title()


def forget_name():
    st.query_params.clear()


# ---------- data ----------
def load():
    songs = db().table("songs").select("*").order("id").execute().data
    votes = db().table("votes").select("*").execute().data
    return songs, votes


def cast(song_id: int, kind: str, current: str):
    if current == kind:  # nogmaals tikken = stem intrekken
        db().table("votes").delete().eq("song_id", song_id).eq("voter", me).execute()
    else:
        db().table("votes").upsert(
            {"song_id": song_id, "voter": me, "vote": kind},
            on_conflict="song_id,voter",
        ).execute()


def withdraw(song_id: int):
    db().table("songs").delete().eq("id", song_id).eq("proposed_by", me).execute()


# ---------- kop ----------
st.title("Zangstonde 🎶")
c1, c2 = st.columns([3, 1])
c1.write(f"Je stemt als **{shown}**")
c2.button("Andere naam", on_click=forget_name)
st.caption(
    "Een liedje gaat er pas uit als er meer ‘eruit’-stemmen zijn dan ‘bescherm’-stemmen. "
    "Eruit liedjes blijven zichtbaar en kunnen terugkomen. Je hebt één stem per liedje; "
    "tik nogmaals op je keuze om je stem in te trekken."
)


# ---------- lijst (ververst automatisch) ----------
@st.fragment(run_every="5s")
def lijst():
    songs, votes = load()
    by_song = {}
    for v in votes:
        by_song.setdefault(v["song_id"], []).append(v)

    inn, uit = [], []
    for s in songs:
        vs = by_song.get(s["id"], [])
        outs = [v["voter"] for v in vs if v["vote"] == "out"]
        keeps = [v["voter"] for v in vs if v["vote"] == "keep"]
        mine = next((v["vote"] for v in vs if v["voter"] == me), "")
        info = dict(song=s, outs=outs, keeps=keeps, mine=mine)
        (uit if len(outs) > len(keeps) else inn).append(info)

    def render(items, section):
        for it in items:
            s = it["song"]
            with st.container(border=True):
                title = s["title"]
                if s.get("proposed_by"):
                    title += f"  · *voorstel van {s['proposed_by'].title()}*"
                st.markdown(f"~~{title}~~" if section == "uit" else title)
                b1, b2 = st.columns(2)
                b1.button(
                    f"Eruit ({len(it['outs'])})",
                    key=f"o{section}{s['id']}",
                    type="primary" if it["mine"] == "out" else "secondary",
                    on_click=cast, args=(s["id"], "out", it["mine"]),
                    use_container_width=True,
                )
                b2.button(
                    f"Bescherm ({len(it['keeps'])})",
                    key=f"k{section}{s['id']}",
                    type="primary" if it["mine"] == "keep" else "secondary",
                    on_click=cast, args=(s["id"], "keep", it["mine"]),
                    use_container_width=True,
                )
                parts = []
                if it["outs"]:
                    parts.append("Eruit: " + ", ".join(n.title() for n in it["outs"]))
                if it["keeps"]:
                    parts.append("Bescherm: " + ", ".join(n.title() for n in it["keeps"]))
                if parts:
                    st.caption(" · ".join(parts))

    st.subheader(f"Op de lijst ({len(inn)})")
    if inn:
        render(inn, "in")
    else:
        st.caption("Nog geen liedjes.")

    st.subheader(f"Eruit gestemd ({len(uit)})")
    if uit:
        render(uit, "uit")
    else:
        st.caption("Nog niets eruit gestemd.")


lijst()

# ---------- voorstellen (buiten het fragment, zodat je typen niet wordt gewist) ----------
st.divider()
st.subheader("Stel een liedje voor")
mine_prop = (
    db().table("songs").select("id,title").eq("proposed_by", me).execute().data
)
if mine_prop:
    p = mine_prop[0]
    st.write(f"Je hebt al voorgesteld: **{p['title']}**")
    st.button("Intrekken", on_click=withdraw, args=(p["id"],))
else:
    with st.form("voorstel", clear_on_submit=True):
        titel = st.text_input("Titel – artiest", max_chars=120)
        if st.form_submit_button("Voorstellen"):
            titel = " ".join(titel.split())
            if titel:
                try:
                    db().table("songs").insert(
                        {"title": titel, "proposed_by": me}
                    ).execute()
                    st.rerun()
                except Exception:
                    st.error("Voorstellen lukte niet. Heb je al een liedje voorgesteld?")
    st.caption("Je kan één liedje voorstellen. Het komt op de lijst en iedereen kan erover stemmen.")
