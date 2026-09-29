import html

import streamlit as st

from ea.config import *

from ea.context import ContextStore

from ea.models import Action, DecisionRecord

from ea.records import DecisionStore

from ea.service import EAService

from ea.futureagi.runtime import evaluate_record, ready as futureagi_ready

from ea.futureagi.optimization import run_optimization, promote_candidate, active_version

from ea.futureagi.simulation import run_simulation



st.set_page_config(page_title='The Gen Academy - EA', page_icon='◈', layout='wide')

st.markdown('''<style>

:root{--off:#fafaf1;--black:#1a1a1a;--gray:#e6e6e6;--purple:#7d83ff;--pm:#6170ff;--orange:#ff5634;--yellow:#ffd500}

.stApp{background:var(--off)!important;color:var(--black)!important}.block-container{max-width:1160px;padding-top:2rem;padding-bottom:5rem}

[data-testid="stSidebar"]{background:var(--black)!important}[data-testid="stSidebar"] *{color:var(--off)!important}[data-testid="stSidebar"] [aria-checked="true"]{background:var(--pm)!important;border-radius:10px}

h1,h2,h3{color:var(--black)!important;letter-spacing:-.035em}.kicker{font-family:monospace;color:var(--orange);letter-spacing:.08em;text-transform:uppercase;font-size:.75rem}.muted{color:#626262}.card{border:2px solid var(--black);border-radius:18px;padding:1.15rem;margin:.8rem 0;background:var(--off);box-shadow:5px 5px 0 var(--black)}.rec{background:var(--gray);border-left:6px solid var(--pm);border-radius:13px;padding:.85rem;margin-top:.8rem}.pill{display:inline-block;border:1.5px solid var(--black);border-radius:999px;padding:.15rem .55rem;margin-right:.3rem;font-family:monospace;font-size:.7rem;background:var(--off)}div[data-testid="stMetric"]{border:2px solid var(--black);border-radius:14px;padding:.7rem 1rem;box-shadow:4px 4px 0 var(--purple);background:var(--off)}.stButton>button{border:2px solid var(--black)!important;border-radius:999px!important;background:var(--off)!important;color:var(--black)!important;font-weight:650!important}.stButton>button:hover{background:var(--yellow)!important}.future{border:2px solid var(--pm);border-radius:16px;padding:1rem;background:#f0f1ff}.resolved{border-left:6px solid var(--yellow)}

</style>''', unsafe_allow_html=True)



@st.cache_resource
def get_service():
    return EAService()

svc = get_service(); store = DecisionStore(); ctx = ContextStore(USER_ID)

with st.sidebar:

    st.markdown('## THE GEN ACADEMY'); st.caption('Executive Assistant / MVP')

    page = st.radio('nav', ['Home','Inbox','Calendar','Activity','Learning','Settings'], label_visibility='collapsed')

    st.divider(); st.caption(('Demo' if DEMO_MODE else 'Live')+' | '+('Shadow' if SHADOW_MODE else 'Autonomy')+' | '+DECISION_POLICY)

    st.caption('Future AGI Evaluate: '+('connected' if futureagi_ready() else 'not configured')); st.caption('Agent: '+active_version())



def save_record(item, decision, user_action, accepted, status="resolved", note=None):
    record = DecisionRecord(
        event=item,
        context_snapshot={"company": ctx.company(), "user": ctx.user()},
        agent_action=decision.action, agent_priority=decision.priority,
        agent_summary=decision.summary, agent_rationale=decision.rationale,
        agent_confidence=decision.confidence, agent_risk=decision.risk,
        agent_version=decision.agent_version, user_action=user_action,
        accepted=accepted, note=note, status=status,
    )
    with st.spinner("Evaluating with Future AGI..."):
        record.evals = evaluate_record(record)
    store.append(record)
    st.session_state.pop("queue", None)
    st.rerun()

def card(item, decision):

    st.html(f'''<div class="card"><div class="kicker">{item.source.value} / {html.escape(item.sender or 'unknown')}</div><h3>{html.escape(item.title)}</h3><div class="muted">{html.escape(item.body[:420])}</div><div class="rec"><span class="pill">{decision.priority.upper()}</span><span class="pill">{decision.confidence:.0%} confidence</span><span class="pill">{decision.autonomy_mode}</span><br><b>EA suggests: {decision.action.value.upper()}</b> - {html.escape(decision.summary)}<div class="muted">{html.escape(decision.rationale)}</div></div></div>''')

    a,b,c,d = st.columns([1,1,1,2])

    if a.button('Agree', key='a'+item.event_id, use_container_width=True): save_record(item, decision, decision.action, True, note='Agreed with EA recommendation')

    if b.button('Delegate', key='d'+item.event_id, use_container_width=True): save_record(item, decision, Action.DELEGATE, decision.action==Action.DELEGATE, note='User chose delegation')

    if c.button('Dismiss', key='x'+item.event_id, use_container_width=True): save_record(item, decision, None, False, status='dismissed', note='Dismissed')

    with d.popover('Choose different action', use_container_width=True):

        value = st.selectbox('Preferred action', [x.value for x in Action], key='s'+item.event_id)

        note = st.text_input('Reason (optional)', key='n'+item.event_id)

        if st.button('Resolve', key='sv'+item.event_id): save_record(item, decision, Action(value), decision.action==Action(value), note=note or 'Corrected')



def refresh_queue():
    with st.spinner("Refreshing assistant..."):
        st.session_state.queue = svc.queue()

def load_queue():
    if "queue" not in st.session_state:
        refresh_queue()
    return st.session_state.queue

try:
    queue = load_queue()
except Exception as exc:
    st.error(f"Could not load assistant: {exc}")
    st.stop()


if page == 'Home':

    user=ctx.user(); name=user.get('profile',{}).get('display_name','there'); metrics=store.metrics()

    st.markdown('<div class="kicker">Executive Assistant / Today</div>', unsafe_allow_html=True); st.title(f'Good to see you, {name}.'); st.write("Here's what deserves your attention.")

    a,b,c,d=st.columns(4); a.metric('High priority',sum(x.priority=='high' for _,x in queue)); b.metric('Upcoming',sum(i.source.value=='calendar' for i,_ in queue)); c.metric('Pending',len(queue)); d.metric('Preference match',f'{metrics["acceptance_rate"]:.0%}' if metrics['count'] else 'Calibrating')

    st.subheader("Today's priorities")
    if st.button("Refresh work queue"):
        refresh_queue(); st.rerun()

    for item,decision in [z for z in queue if z[1].priority!='low'][:5]: card(item,decision)

elif page == 'Inbox':

    st.markdown('<div class="kicker">Communication</div>',unsafe_allow_html=True); st.title('Inbox'); st.caption('Only unresolved Gmail and Slack decisions remain here.')

    for item,decision in queue:

        if item.source.value in ('gmail','slack'): card(item,decision)

elif page == 'Calendar':

    st.markdown('<div class="kicker">Time</div>',unsafe_allow_html=True); st.title('Calendar')

    for item,decision in queue:

        if item.source.value=='calendar' or decision.action==Action.SCHEDULE: card(item,decision)

elif page == 'Activity':

    st.markdown('<div class="kicker">Decision history</div>'); st.title('Activity'); rows=store.all()

    if not rows: st.info('Resolve a card and it will move here.')

    for r in reversed(rows):

        user_action=r.user_action.value.upper() if r.user_action else r.status.upper(); score=r.evals.get('action_accuracy') if r.evals else None

        st.html(f'''<div class="card resolved"><div class="kicker">{r.event.source.value} / {r.resolved_at.strftime('%d %b %H:%M')}</div><h3>{html.escape(r.event.title)}</h3><b>EA:</b> {r.agent_action.value.upper()} &nbsp; → &nbsp; <b>You:</b> {user_action}<br><span class="muted">Agent {r.agent_version} · {r.agent_confidence:.0%} confidence{(' · Future AGI action score '+str(round(score,2))) if score is not None else ''}</span></div>''')

elif page == 'Learning':

    st.markdown('<div class="kicker">Future AGI / Continuous improvement</div>',unsafe_allow_html=True); st.title('Learning')

    tabs=st.tabs(['Overview','Observe','Evaluate','Optimize','Simulate']); rows=store.all(); metrics=store.metrics()

    with tabs[0]:

        a,b,c=st.columns(3); a.metric('Resolved decisions',metrics['count']); b.metric('Preference match',f'{metrics["acceptance_rate"]:.0%}'); c.metric('Active agent',active_version())

        st.markdown('<div class="future"><b>Improvement loop</b><br>Observe → Evaluate → Error Feed → Optimize → Simulate / Replay → Deploy → Production feedback</div>',unsafe_allow_html=True)

    with tabs[1]:

        st.subheader('Observe')

        if svc.observe.get('enabled'): st.success(f"Tracing is connected to Future AGI project: {svc.observe.get('project')}")

        else: st.warning('Future AGI Observe is not active. '+svc.observe.get('reason',''))

        st.caption('Observe is optional and never blocks Evaluate/Optimize. HTTP transport is used when enabled.')

    with tabs[2]:

        st.subheader('Evaluate'); scored=[r for r in rows if r.evals and r.evals.get('enabled')]

        if not futureagi_ready(): st.warning('Add FI_API_KEY + FI_SECRET_KEY and set FUTUREAGI_ENABLED=true.')

        elif not scored: st.info('Resolve decisions to run Future AGI action-accuracy and groundedness evals.')

        else:

            acc=[r.evals.get('action_accuracy') for r in scored if r.evals.get('action_accuracy') is not None]; grounded=[r.evals.get('groundedness') for r in scored if r.evals.get('groundedness') is not None]

            a,b=st.columns(2); a.metric('Action agreement',f'{sum(acc)/len(acc):.0%}' if acc else '—'); b.metric('Rationale groundedness',f'{sum(grounded)/len(grounded):.0%}' if grounded else '—')

            st.markdown("#### Evaluation details")

            for record in reversed(scored):
                agent_action = record.agent_action.value.upper()

                human_action = (
                    record.user_action.value.upper()
                    if record.user_action
                    else record.status.upper()
                )

                accuracy = record.evals.get(
                    "action_accuracy"
                )

                groundedness = record.evals.get(
                    "groundedness"
                )

                reason = record.evals.get(
                    "groundedness_reason",
                    "",
                )

                accuracy_text = (
                    f"{accuracy:.0%}"
                    if accuracy is not None
                    else "Not available"
                )

                groundedness_text = (
                    f"{groundedness:.0%}"
                    if groundedness is not None
                    else "Not available"
                )

                st.html(
                    f"""
                    <div class="card">

                        <div class="kicker">
                            {record.event.source.value.upper()}
                        </div>

                        <h3>
                            {html.escape(record.event.title)}
                        </h3>

                        <div>
                            <b>EA:</b>
                            {agent_action}

                            &nbsp; &rarr; &nbsp;

                            <b>You:</b>
                            {human_action}
                        </div>

                        <div style="margin-top: 0.7rem;">
                            <span class="pill">
                                Action agreement:
                                {accuracy_text}
                            </span>

                            <span class="pill">
                                Groundedness:
                                {groundedness_text}
                            </span>
                        </div>

                        {
                            f'''
                            <div
                                class="muted"
                                style="margin-top: 0.7rem;"
                            >
                                {html.escape(reason)}
                            </div>
                            '''
                            if reason
                            else ""
                        }

                    </div>
                    """
                )
    with tabs[3]:

        st.subheader('Optimize'); st.write('Future AGI agent-opt uses resolved human decisions as labeled examples. The winning action-selection prompt is saved and injected as learned guidance on later EA decisions.')

        labeled=sum(1 for r in rows if r.user_action); st.metric('Labeled examples',labeled)

        if st.button('Run Future AGI optimization', disabled=not futureagi_ready()):

            with st.spinner('Optimizing prompt against your decisions...'):

                try:

                    result=run_optimization(rows)

                    if result.get('ok'):
                        st.success(f"Candidate generated. Score: {result['final_score']:.3f} on {result['examples']} examples")
                        st.code(result['best_prompt'])
                        if st.button('Promote candidate to EA V2'):
                            promoted=promote_candidate()
                            if promoted.get('ok'):
                                st.session_state.pop('queue',None); get_service.clear(); st.success(promoted['message']); st.rerun()
                            else: st.warning(promoted.get('message'))

                    else: st.warning(result.get('message'))

                except Exception as exc: st.error(f'Optimization failed: {exc}')

    with tabs[4]:

        st.subheader('Simulate'); st.write('Runs the EA against the Future AGI chat simulation configured in FUTUREAGI_SIMULATION_ID. Personas, scenarios, transcripts and eval results live in Future AGI.')

        if not FUTUREAGI_SIMULATION_ID: st.info('Create a chat simulation in Future AGI, then set FUTUREAGI_SIMULATION_ID to its exact run-test name.')

        if st.button('Run synthetic-user simulation', disabled=not(futureagi_ready() and FUTUREAGI_SIMULATION_ID)):

            with st.spinner('Running Future AGI simulation...'):

                try:

                    result=run_simulation(); st.success(result.get('message')) if result.get('ok') else st.warning(result.get('message'))

                except Exception as exc: st.error(f'Simulation failed: {exc}')

elif page == 'Settings':

    st.markdown('<div class="kicker">Configuration</div>',unsafe_allow_html=True); st.title('Settings'); user=ctx.user(); profile=user.get('profile',{}); a,b=st.columns(2)

    profile['display_name']=a.text_input('Display name',profile.get('display_name','')); profile['role']=b.text_input('Role',profile.get('role','')); profile['timezone']=st.text_input('Timezone',profile.get('timezone','Asia/Kolkata')); prefs=st.text_area('Explicit preferences','\n'.join(user.get('explicit_preferences',[])),height=170)

    if st.button('Save settings',type='primary'): user['profile']=profile; user['explicit_preferences']=[x.strip() for x in prefs.splitlines() if x.strip()]; ctx.save_user(USER_ID,user); st.session_state.pop('queue',None); st.success('Saved')
