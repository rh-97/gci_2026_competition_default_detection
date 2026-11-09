"""Isolate the second-pass patience/cap change from changes to features."""
import round2 as r

if __name__=='__main__':
    train,test,y,split=r.load()
    if not (r.ART/'budget_control_plan.json').exists():
        r.dump(r.ART/'budget_control_plan.json',dict(name='r2_cat_budget_control',kind='cat',features='lean',
            params=dict(depth=5,l2_leaf_reg=8,random_strength=.5),source='improvements/round2/budget_control.py',
            hypothesis='Hold model parameters and features fixed; isolate patience 150 to 200 and cap 3000 to 4500.'))
    spec=r.read(r.ART/'budget_control_plan.json')
    r.screen_one(spec,train,y,split)
