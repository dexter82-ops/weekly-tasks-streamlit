
import streamlit as st
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
import uuid
import os

DATA_PATH = os.path.join("data", "tasks.csv")
STATUSES = ["Backlog", "This Week", "In Progress", "Done"]
WEEKDAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
RECUR_OPTS = ["None","Weekly","Biweekly","Monthly"]

@st.cache_data(ttl=5.0)
def load_tasks():
    if not os.path.exists(DATA_PATH):
        os.makedirs("data", exist_ok=True)
        cols = ["id","title","description","status","priority","effort","weekday","due_date","recur","tags","created_at","updated_at"]
        df = pd.DataFrame(columns=cols)
        df.to_csv(DATA_PATH, index=False)
        return df
    df = pd.read_csv(DATA_PATH, dtype=str).fillna("")
    return df

def save_tasks(df):
    df.to_csv(DATA_PATH, index=False)
    load_tasks.clear()

def new_id():
    return str(uuid.uuid4())[:8]

def ensure_types(df):
    for c in ["priority","effort"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(3).astype(int)
    # make sure required cols exist
    required = ["id","title","description","status","priority","effort","weekday","due_date","recur","tags","created_at","updated_at"]
    for c in required:
        if c not in df.columns:
            df[c] = ""
    return df

def add_recurring_if_done(row):
    recur = (row.get("recur") or "None").strip()
    status = row.get("status","")
    if status != "Done" or recur == "None":
        return None
    # Compute next occurrence
    due = (row.get("due_date") or "").strip()
    wd = row.get("weekday","Mon")
    base_date = None
    if due:
        try:
            base_date = datetime.fromisoformat(due).date()
        except:
            base_date = date.today()
    else:
        base_date = date.today()
        target = WEEKDAYS.index(wd if wd in WEEKDAYS else "Mon")
        while base_date.weekday() != target:
            base_date += timedelta(days=1)

    if recur == "Weekly":
        next_date = base_date + timedelta(weeks=1)
    elif recur == "Biweekly":
        next_date = base_date + timedelta(weeks=2)
    elif recur == "Monthly":
        next_date = base_date + relativedelta(months=1)
    else:
        return None

    new_row = dict(row)
    new_row["id"] = new_id()
    new_row["status"] = "This Week"
    new_row["created_at"] = datetime.now().isoformat(timespec="seconds")
    new_row["updated_at"] = new_row["created_at"]
    new_row["due_date"] = datetime.combine(next_date, datetime.min.time()).isoformat(timespec="seconds")
    new_row["weekday"] = WEEKDAYS[next_date.weekday()]
    return new_row

st.set_page_config(page_title="Weekly Tasks", page_icon="🗓️", layout="wide")

st.title("🗓️ Weekly Tasks — Planificateur")
st.caption("Planifie ta semaine, priorise, suis l'avancement, et gère les récurrences.")

df = load_tasks()
df = ensure_types(df)

# Sidebar: filters & import/export
with st.sidebar:
    st.header("🔎 Filtres")
    txt = st.text_input("Recherche texte (titre / description / tags)", "")
    sel_status = st.multiselect("Statuts", STATUSES, default=STATUSES)
    sel_days = st.multiselect("Jours", WEEKDAYS, default=WEEKDAYS)
    tags_q = st.text_input("Filtre tags (séparés par ;)", "")
    st.divider()
    st.subheader("📤 Export / 📥 Import CSV")
    st.download_button("Exporter le CSV", df.to_csv(index=False).encode("utf-8"), file_name="tasks.csv", mime="text/csv")
    uploaded = st.file_uploader("Importer un CSV (remplace)", type=["csv"])
    if uploaded is not None:
        new_df = pd.read_csv(uploaded, dtype=str).fillna("")
        save_tasks(new_df)
        st.success("CSV importé avec succès. Recharge la page si besoin.")

# Apply filters
mask = df["status"].isin(sel_status) & df["weekday"].isin(sel_days)
if txt:
    txtlower = txt.lower()
    mask &= (
        df["title"].str.lower().str.contains(txtlower) |
        df["description"].str.lower().str.contains(txtlower) |
        df["tags"].str.lower().str.contains(txtlower)
    )
if tags_q:
    for t in [t.strip().lower() for t in tags_q.split(";") if t.strip()]:
        mask &= df["tags"].str.lower().str.contains(t)

fdf = df[mask].copy()

# Add quick task
with st.expander("➕ Ajouter une tâche rapide"):
    c1,c2,c3,c4,c5 = st.columns([3,3,2,2,2])
    with c1:
        t_title = st.text_input("Titre", key="new_title")
    with c2:
        t_desc = st.text_input("Description", key="new_desc")
    with c3:
        t_status = st.selectbox("Statut", STATUSES, index=1, key="new_status")
    with c4:
        t_priority = st.number_input("Priorité (1-5)", min_value=1, max_value=5, value=3, step=1, key="new_priority")
    with c5:
        t_effort = st.number_input("Effort (pts)", min_value=1, max_value=8, value=3, step=1, key="new_effort")
    c6,c7,c8 = st.columns([2,2,3])
    with c6:
        t_day = st.selectbox("Jour", WEEKDAYS, index=0, key="new_day")
    with c7:
        t_recur = st.selectbox("Récurrence", RECUR_OPTS, index=0, key="new_recur")
    with c8:
        t_tags = st.text_input("Tags (séparés par ;)", key="new_tags")

    if st.button("Ajouter"):
        if t_title.strip() == "":
            st.warning("Le titre est requis.")
        else:
            now = datetime.now().isoformat(timespec="seconds")
            row = {
                "id": new_id(),
                "title": t_title.strip(),
                "description": t_desc.strip(),
                "status": t_status,
                "priority": int(t_priority),
                "effort": int(t_effort),
                "weekday": t_day,
                "due_date": "",
                "recur": t_recur,
                "tags": t_tags.strip(),
                "created_at": now,
                "updated_at": now
            }
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            save_tasks(df)
            st.success("Tâche ajoutée ✅")

st.divider()

# Week board
st.subheader("📅 Tableau hebdomadaire")
cols = st.columns(len(WEEKDAYS), gap="small")

for i, day in enumerate(WEEKDAYS):
    with cols[i]:
        st.markdown(f"**{day}**")
        day_df = fdf[fdf["weekday"] == day].sort_values(["priority","title"])
        for _, row in day_df.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['title']}**")
                st.caption(row["description"])
                c1, c2, c3 = st.columns([2,2,1])
                with c1:
                    new_status = st.selectbox("Statut", STATUSES, index=STATUSES.index(row["status"]), key=f"status_{row['id']}")
                with c2:
                    new_prio = st.slider("Priorité", 1,5,int(row["priority"]), key=f"prio_{row['id']}")
                with c3:
                    new_eff = st.number_input("Pts", 1, 8, int(row["effort"]), key=f"eff_{row['id']}")
                c4, c5 = st.columns([2,1])
                with c4:
                    new_tags = st.text_input("Tags", value=row["tags"], key=f"tags_{row['id']}")
                with c5:
                    new_day = st.selectbox("Jour", WEEKDAYS, index=WEEKDAYS.index(row["weekday"]), key=f"day_{row['id']}")

                c6, c7, c8 = st.columns([1,1,1])
                with c6:
                    new_recur = st.selectbox("Récurrence", RECUR_OPTS, index=RECUR_OPTS.index((row.get('recur') or 'None')), key=f"recur_{row['id']}")
                with c7:
                    due_val = row.get("due_date","")
                    new_due = st.text_input("Échéance (YYYY-MM-DD)", value=(due_val[:10] if isinstance(due_val, str) and due_val else ""), key=f"due_{row['id']}")
                with c8:
                    if st.button("🗑️ Supprimer", key=f"del_{row['id']}"):
                        df = df[df["id"] != row["id"]]
                        save_tasks(df)
                        st.stop()

                if st.button("💾 Sauver", key=f"save_{row['id']}"):
                    idx = df.index[df["id"] == row["id"]]
                    if len(idx):
                        i0 = idx[0]
                        df.at[i0,"status"] = new_status
                        df.at[i0,"priority"] = int(new_prio)
                        df.at[i0,"effort"] = int(new_eff)
                        df.at[i0,"tags"] = new_tags
                        df.at[i0,"weekday"] = new_day
                        df.at[i0,"recur"] = new_recur
                        if new_due:
                            try:
                                d = datetime.fromisoformat(new_due.strip())
                                df.at[i0,"due_date"] = d.isoformat(timespec="seconds")
                            except:
                                df.at[i0,"due_date"] = new_due.strip()
                        df.at[i0,"updated_at"] = datetime.now().isoformat(timespec="seconds")
                        # Handle recurrence duplication
                        if new_status == "Done":
                            child = add_recurring_if_done(df.loc[i0].to_dict())
                            if child is not None:
                                df = pd.concat([df, pd.DataFrame([child])], ignore_index=True)
                        save_tasks(df)
                        st.success("Modifications enregistrées ✅")
                        st.experimental_rerun()

st.divider()

# Insights
st.subheader("📈 Insights (mini)")
cc1, cc2, cc3, cc4 = st.columns(4)
with cc1:
    st.metric("Tâches Backlog", int((df["status"]=="Backlog").sum()))
with cc2:
    st.metric("Prévu cette semaine", int((df["status"]=="This Week").sum()))
with cc3:
    st.metric("En cours", int((df["status"]=="In Progress").sum()))
with cc4:
    st.metric("Terminées", int((df["status"]=="Done").sum()))

st.caption("Astuce : utilise les filtres pour te focaliser sur un segment (ex: `contrathèque;juridique`).")
