def choose_autonomy_mode(confidence:float,risk:float,shadow_mode:bool)->str:
 if shadow_mode:return 'ask' if confidence<.60 else 'propose'
 if risk>=.55 or confidence<.60:return 'ask'
 if confidence>=.90 and risk<=.20:return 'act'
 return 'propose'
