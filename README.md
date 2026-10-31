# Zangstonde (Streamlit + Supabase)

## 1. Tabellen en startlijst aanmaken
1. Supabase > jouw project > **SQL Editor** > **New query**.
2. Plak de inhoud van `schema.sql` en klik **Run**.
3. Check onder **Table Editor**: `songs` bevat 15 liedjes, `votes` is leeg.

## 2. Sleutels ophalen
Supabase > **Project Settings > API Keys** (of **API**):
- **Project URL** (begint met `https://` en eindigt op `.supabase.co`)
- de **secret key** (`sb_secret_...`), of in oudere projecten de `service_role` key

Gebruik NIET de publieke/anon key. De secret key blijft op de server van Streamlit en mag
**nooit** in GitHub of in een bericht terechtkomen.

## 3. Op GitHub zetten
1. Nieuwe repository (privé mag), bv. `zangstonde`.
2. Upload `app.py` en `requirements.txt`. (`schema.sql` en deze README mogen erbij, maar zijn niet nodig.)
3. Zet GEEN sleutels in de repository.

## 4. Online zetten
1. Ga naar https://share.streamlit.io en meld je aan met GitHub.
2. **Create app** > kies je repository, branch `main`, bestand `app.py`.
3. **Advanced settings > Secrets**, plak (met jouw waarden):

   ```
   SUPABASE_URL = "https://xxxx.supabase.co"
   SUPABASE_KEY = "sb_secret_..."
   ```
4. **Deploy**. Je krijgt een link zoals `https://zangstonde.streamlit.app`.

## 5. Delen
Stuur de link naar de familie. Iedereen vult zijn voornaam in en kan stemmen, zonder account.
Wie op een ander toestel dezelfde voornaam gebruikt, stemt als dezelfde persoon.

## Liedjes later toevoegen of verwijderen
Supabase > **Table Editor > songs**: rij toevoegen of verwijderen. Bij verwijderen verdwijnen ook de stemmen.
Alle stemmen wissen: `delete from votes;` in de SQL Editor.
