"""Separate mission editor; ordinary condition/rule/action graphs are untouched."""
import copy
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from engine import Graph, dump, strict_json, atomic_write
from missions import MissionProject, tutorial_project, PREDICATES, validate_mission

TEXT={
 'en':{'title':'Mission / campaign','open':'Open project','save':'Save project','zip':'Export bundle ZIP','pack':'Import pack','operation':'Import operation','edit_operation':'Edit operation parameters','add':'Add stage','remove':'Remove stage','apply':'Apply stage','requirement':'Add / edit requirement','undo':'Undo','redo':'Redo','validate':'Validate','success':'After verified success','failure':'On failure — stop for review','help':'Mission stages await verified completion. Rule action wires do not sequence work. Final stock, equipment, soil and arrival requirements are checked again at mission end. Task-success requirements are historical receipts. Unknown observations never succeed. Stage retries: 0; operation retries retain their own budgets. Install ZIP in resources/samcnpc/behaviors, reload, then /samcnpc behavior mission start <NPC> <mission-id>. PAUSE / RESUME / CANCEL are mission controls. Restart uncertainty or changed packs requires review; no blind assignment replay.','preview':'JSON preview','new':'Three-stage tutorial','id':'Stage ID','timeout':'Timeout (ticks)','refs':'Completion requirement IDs (comma separated)','next':'Success destination (empty = finish)','mission':'Mission ID','dimension':'Dimension','context':'Operation (explicit admission)'} ,
 'pl':{'title':'Misja / kampania','open':'Otwórz projekt','save':'Zapisz projekt','zip':'Eksportuj pakiet ZIP','pack':'Importuj paczkę','operation':'Importuj operację','edit_operation':'Edytuj parametry operacji','add':'Dodaj etap','remove':'Usuń etap','apply':'Zastosuj etap','requirement':'Dodaj / edytuj wymaganie','undo':'Cofnij','redo':'Ponów','validate':'Waliduj','success':'Po potwierdzonym sukcesie','failure':'Po błędzie — zatrzymaj do przeglądu','help':'Etapy czekają na potwierdzone wykonanie. Przewody akcji reguł nie tworzą kolejki. Końcowy stan zapasów, wyposażenia, gleby i położenia jest sprawdzany ponownie na końcu misji. Sukces zadania jest historycznym potwierdzeniem. Nieznana obserwacja nie oznacza sukcesu. Ponowienia etapu: 0; operacja zachowuje własne limity. ZIP umieść w resources/samcnpc/behaviors, wykonaj reload, potem /samcnpc behavior mission start <NPC> <id-misji>. PAUSE / RESUME / CANCEL sterują misją. Niepewny restart lub zmiana paczki wymaga przeglądu, bez ponownego zlecania w ciemno.','preview':'Podgląd JSON','new':'Samouczek trzech etapów','id':'ID etapu','timeout':'Limit czasu (ticki)','refs':'ID wymagań ukończenia (po przecinku)','next':'Etap po sukcesie (puste = koniec)','mission':'ID misji','dimension':'Wymiar','context':'Operacja (jawne zlecenie)'},
 'de':{'title':'Mission / Kampagne','open':'Projekt öffnen','save':'Projekt speichern','zip':'ZIP-Bündel exportieren','pack':'Paket importieren','operation':'Operation importieren','edit_operation':'Operationsparameter bearbeiten','add':'Stufe hinzufügen','remove':'Stufe entfernen','apply':'Stufe übernehmen','requirement':'Anforderung hinzufügen / bearbeiten','undo':'Rückgängig','redo':'Wiederholen','validate':'Prüfen','success':'Nach bestätigtem Erfolg','failure':'Bei Fehler — zur Prüfung anhalten','help':'Stufen warten auf bestätigten Abschluss. Aktionsverbindungen bilden keine Reihenfolge. Endbestand, Ausrüstung, Boden und Zielposition werden am Missionsende erneut geprüft. Aufgabenerfolg ist ein historischer Beleg. Unbekannte Beobachtungen sind niemals Erfolg. Stufenwiederholungen: 0; Operationen behalten ihre eigenen Grenzen. ZIP unter resources/samcnpc/behaviors installieren, reload ausführen, dann /samcnpc behavior mission start <NPC> <Missions-ID>. PAUSE / RESUME / CANCEL steuern die Mission. Unklarer Neustart oder geänderte Pakete erfordern Prüfung, keine blinde erneute Zuweisung.','preview':'JSON-Vorschau','new':'Dreistufiges Tutorial','id':'Stufen-ID','timeout':'Zeitlimit (Ticks)','refs':'Abschlussanforderungen (durch Komma getrennt)','next':'Erfolgsziel (leer = Ende)','mission':'Missions-ID','dimension':'Dimension','context':'Operation (explizite Zulassung)'}
}
for language,pack,operation in [('en','Referenced pack','Operation'),('pl','Przypisana paczka','Operacja'),('de','Zugewiesenes Paket','Operation')]:
    TEXT[language]['pack_reference']=pack
    TEXT[language]['operation_column']=operation

class MissionWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app); self.app=app; self.geometry('1280x860'); self.project=tutorial_project()
        self.history=[]; self.future=[]; self.labels=[]; self.vars={}; self.selected=0
        self.transient(app)
        bar=ttk.Frame(self);bar.pack(fill='x')
        for key,command in [('new',self.new),('open',self.open),('save',self.save),('zip',self.export),('pack',self.import_pack),('undo',self.undo),('redo',self.redo),('validate',self.validate)]:
            self.button(bar,key,command).pack(side='left',padx=3,pady=4)
        self.help=ttk.Label(self,wraplength=1180);self.help.pack(fill='x',padx=12,pady=8)
        split=ttk.Panedwindow(self,orient='horizontal');split.pack(fill='both',expand=True)
        left=ttk.Frame(split);right=ttk.Frame(split);split.add(left,weight=2);split.add(right,weight=3)
        diagram=ttk.Frame(left);diagram.pack(fill='x')
        self.canvas=tk.Canvas(diagram,bg='#111c29',height=220);self.canvas.grid(row=0,column=0,sticky='ew')
        diagram.columnconfigure(0,weight=1)
        vertical=ttk.Scrollbar(diagram,orient='vertical',command=self.canvas.yview);vertical.grid(row=0,column=1,sticky='ns')
        horizontal=ttk.Scrollbar(diagram,orient='horizontal',command=self.canvas.xview);horizontal.grid(row=1,column=0,sticky='ew')
        self.canvas.configure(yscrollcommand=vertical.set,xscrollcommand=horizontal.set)
        failure=ttk.Label(left);failure.pack(fill='x',padx=8,pady=4);self.labels.append((failure,'failure'))
        self.canvas.bind('<Button-1>',self.select_canvas)
        self.list=ttk.Treeview(left,columns=('pack','operation'),show='tree headings',height=7)
        self.list.heading('#0',text='ID');self.list.heading('pack',text='Pack');self.list.heading('operation',text='Operation')
        self.list.column('#0',width=95);self.list.column('pack',width=170);self.list.column('operation',width=150)
        self.list.pack(fill='both',expand=True);self.list.bind('<<TreeviewSelect>>',self.select)
        actions=ttk.Frame(left);actions.pack(fill='x')
        for key,command in [('add',self.add),('remove',self.remove),('requirement',self.requirement)]:self.button(actions,key,command).pack(side='left')
        form=ttk.Frame(right,padding=8);form.pack(fill='x')
        for key in ('mission','dimension','id','pack','timeout','refs','next','context'):
            row=ttk.Frame(form);row.pack(fill='x',pady=2);label=ttk.Label(row,width=35);label.pack(side='left');self.labels.append((label,'pack_reference' if key=='pack' else key))
            variable=tk.StringVar();self.vars[key]=variable
            if key=='pack':self.pack_input=ttk.Combobox(row,textvariable=variable,state='readonly');widget=self.pack_input
            else:widget=ttk.Entry(row,textvariable=variable,state='readonly' if key=='context' else 'normal')
            widget.pack(side='left',fill='x',expand=True)
        actions=ttk.Frame(right);actions.pack(fill='x')
        for key,command in [('apply',self.apply),('operation',self.import_operation),('edit_operation',self.edit_operation)]: self.button(actions,key,command).pack(side='left')
        self.preview=tk.Text(right,wrap='none',height=24);self.preview.pack(fill='both',expand=True,padx=8,pady=8)
        self.status=ttk.Label(self);self.status.pack(fill='x',padx=8)
        self.bind('<Control-z>',lambda e:self.undo());self.bind('<Control-y>',lambda e:self.redo())
        self.bind('<Control-s>',lambda e:self.save())
        self.translate();self.refresh()
    def tr(self,key):return TEXT[self.app.lang].get(key,key)
    def button(self,parent,key,command):
        button=ttk.Button(parent,command=lambda:self.safe(command));self.labels.append((button,key));return button
    def safe(self,command):
        try:command()
        except (OSError,ValueError,TypeError,KeyError) as error: self.status.configure(text=str(error));messagebox.showerror(self.tr('title'),str(error),parent=self)
    def translate(self):
        self.title('SAMCNPC — '+self.tr('title'))
        for label,key in self.labels:label.configure(text=self.tr(key))
        self.help.configure(text=self.tr('help'));self.draw()
        self.list.heading('pack',text=self.tr('pack_reference'));self.list.heading('operation',text=self.tr('operation_column'))
    def remember(self):self.history.append(self.project.project());self.history=self.history[-64:];self.future.clear()
    def refresh(self):
        stages=self.project.mission['stages'];self.selected=min(self.selected,max(0,len(stages)-1))
        self.list.delete(*self.list.get_children())
        for i,s in enumerate(stages):self.list.insert('', 'end',iid=str(i),text=s['id'],values=(s['pack'],s.get('operation',{}).get('type','—')))
        self.pack_input.configure(values=[p['id'] for p in self.project.packs])
        if stages:self.list.selection_set(str(self.selected));self.load_fields()
        self.preview.configure(state='normal');self.preview.delete('1.0','end');self.preview.insert('1.0',dump(self.project.mission));self.preview.configure(state='disabled')
        self.draw()
    def draw(self):
        if not hasattr(self,'canvas'):return
        self.canvas.delete('all');self.node_ranges=[]
        for i,s in enumerate(self.project.mission['stages']):
            x=15+(i%3)*175;y=12+(i//3)*90
            self.canvas.create_rectangle(x,y,x+160,y+46,fill='#154663',outline='#20bcea')
            self.canvas.create_text(x+80,y+14,text=s['id'],fill='white');self.canvas.create_text(x+80,y+32,text=s['pack'],fill='#aae7ff',width=150)
            self.node_ranges.append((x,y,x+160,y+46,i))
            self.canvas.create_text(x+80,y+64,text=(self.tr('success')+' → '+str(s['success'])) if s.get('success') else '✓',fill='#b8e596',width=168,font=('Segoe UI',8))
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        positions={s['id']:self.node_ranges[i] for i,s in enumerate(self.project.mission['stages'])}
        for s in self.project.mission['stages']:
            if s.get('success') in positions:
                x,y,x2,y2,_=positions[s['id']]; tx,ty,tx2,ty2,_=positions[s['success']]
                self.canvas.create_line(x2,y+23,tx,ty+23,arrow='last',fill='#b8e596',width=2)
    def select_canvas(self,e):
        cx=self.canvas.canvasx(e.x);cy=self.canvas.canvasy(e.y)
        for x,y,x2,y2,i in self.node_ranges:
            if x<=cx<=x2 and y<=cy<=y2:self.selected=i;self.list.selection_set(str(i));self.load_fields();break
    def select(self,e=None):
        selection=self.list.selection()
        if selection and int(selection[0]) != self.selected:
            self.selected=int(selection[0]);self.load_fields()
    def load_fields(self):
        s=self.project.mission['stages'][self.selected]
        values={'mission':self.project.mission['id'],'dimension':self.project.mission['dimensionId'],'id':s['id'],'pack':s['pack'],'timeout':s['timeoutTicks'],'refs':','.join(s['completion']),'next':s.get('success') or '', 'context':s.get('operation',{}).get('type','—')}
        for key,value in values.items():self.vars[key].set(value)
    def apply(self):
        updated=copy.deepcopy(self.project.mission);s=updated['stages'][self.selected]
        s.update(id=self.vars['id'].get(),pack=self.vars['pack'].get(),timeoutTicks=int(self.vars['timeout'].get()),completion=[x.strip() for x in self.vars['refs'].get().split(',') if x.strip()],success=self.vars['next'].get() or None)
        updated['id']=self.vars['mission'].get();updated['dimensionId']=self.vars['dimension'].get()
        self.remember();self.project.mission=updated;self.refresh()
    def add(self):
        self.remember(); stages=self.project.mission['stages'];index=len(stages)+1
        while any(s['id']==f'stage_{index}' for s in stages):index+=1
        if stages:stages[-1]['success']=f'stage_{index}'
        stages.append({'id':f'stage_{index}','pack':self.project.packs[0]['id'],'completion':[],'timeoutTicks':1200,'retries':0,'success':None})
        self.selected=len(stages)-1;self.refresh()
    def remove(self):
        if not self.project.mission['stages']:return
        self.remember();stage=self.project.mission['stages'].pop(self.selected)
        for s in self.project.mission['stages']:
            if s.get('success')==stage['id']:s['success']=stage.get('success')
        self.refresh()
    def undo(self):
        if self.history:self.future.append(self.project.project());v=self.history.pop();self.project=MissionProject(v['mission'],v['packs']);self.refresh()
    def redo(self):
        if self.future:self.history.append(self.project.project());v=self.future.pop();self.project=MissionProject(v['mission'],v['packs']);self.refresh()
    def new(self):self.remember();self.project=tutorial_project();self.selected=0;self.refresh()
    def open(self):
        file=filedialog.askopenfilename(parent=self,filetypes=[('Mission project','*.sammission')])
        if file:self.remember();self.project=MissionProject.read(strict_json(Path(file).read_text(encoding='utf-8'),project=True));self.refresh()
    def save(self):
        file=filedialog.asksaveasfilename(parent=self,defaultextension='.sammission')
        if file:atomic_write(Path(file),dump(self.project.project()))
    def export(self):
        self.project.validate();file=filedialog.asksaveasfilename(parent=self,defaultextension='.zip')
        if file:self.project.export(file);self.status.configure(text=str(file))
    def validate(self):self.project.validate();self.status.configure(text='LOCAL PASS — Forge reload/admission remains authoritative')
    def import_pack(self):
        file=filedialog.askopenfilename(parent=self,filetypes=[('Pack / graph','*.json *.samgraph')])
        if not file:return
        value=strict_json(Path(file).read_text(encoding='utf-8'),project=True)
        pack=Graph.from_project(value).to_pack() if value.get('format')=='samcnpc-studio' else value
        self.remember();self.project.packs=[p for p in self.project.packs if p['id']!=pack['id']]+[pack];self.refresh()
    def import_operation(self):
        file=filedialog.askopenfilename(parent=self,filetypes=[('Registered operation document','*.json')])
        if file:self.remember();self.project.mission['stages'][self.selected]['operation']=strict_json(Path(file).read_text(encoding='utf-8'));self.refresh()
    def scalar_dialog(self,title,value,callback,choices=None):
        dialog=tk.Toplevel(self);dialog.title(title);dialog.transient(self);fields=[]
        frame=ttk.Frame(dialog,padding=12);frame.pack(fill='both',expand=True)
        def add(data,path=()):
            if isinstance(data,dict):
                for k,v in data.items():add(v,path+(k,))
            elif isinstance(data,list):
                for i,v in enumerate(data):add(v,path+(i,))
            else:
                row=ttk.Frame(frame);row.pack(fill='x');ttk.Label(row,text='.'.join(map(str,path)),width=36).pack(side='left')
                var=tk.StringVar(value='' if data is None else str(data));ttk.Entry(row,textvariable=var,width=42).pack(side='left');fields.append((path,data,var))
        add(value)
        def commit():
            result=copy.deepcopy(value)
            for path,old,var in fields:
                target=result
                for key in path[:-1]:target=target[key]
                raw=var.get();target[path[-1]]=int(raw) if type(old) is int else float(raw) if type(old) is float else raw.lower()=='true' if type(old) is bool else raw
            callback(result);dialog.destroy()
        ttk.Button(frame,text=self.tr('apply'),command=lambda:self.safe(commit)).pack(pady=8)
    def edit_operation(self):
        s=self.project.mission['stages'][self.selected]
        if 'operation' not in s:return
        def commit(value):self.remember();s['operation']=value;self.refresh()
        self.scalar_dialog(self.tr('edit_operation'),s['operation'],commit)
    def requirement(self):
        dialog=tk.Toplevel(self);dialog.title(self.tr('requirement'));dialog.transient(self)
        name=tk.StringVar(value='requirement_'+str(len(self.project.mission['requirements'])+1));kind=tk.StringVar(value=PREDICATES[0])
        names=[r['id'] for r in self.project.mission['requirements']]
        ttk.Combobox(dialog,textvariable=name,values=names).pack(padx=12,pady=8)
        ttk.Combobox(dialog,textvariable=kind,values=PREDICATES,state='readonly').pack(padx=12,pady=8)
        def choose():
            existing=next((r for r in self.project.mission['requirements'] if r['id']==name.get()),None)
            presets={'inventory_count':{'query':'minecraft:coal','count':2,'minimumDurability':0.0},'equipment_matches':{'query':'@axe','destination':'MAIN_HAND','minimumDurability':0.2},'at_position':{'position':{'x':0.5,'y':65.0,'z':0.5},'radius':0.75},'destination_count':{'position':{'x':3,'y':65,'z':0},'itemId':'minecraft:coal','count':2},'soil_prepared':{'cells':[{'x':0,'y':64,'z':0}]},'task_success':{'stageId':self.project.mission['stages'][self.selected]['id']}}
            value=existing['predicate'] if existing and existing['predicate']['type']==kind.get() else {'type':kind.get(),**presets[kind.get()]}
            def commit(predicate):
                self.remember();self.project.mission['requirements']=[r for r in self.project.mission['requirements'] if r['id']!=name.get()]+[{'id':name.get(),'predicate':predicate}];self.refresh()
            dialog.destroy();self.scalar_dialog(self.tr('requirement'),value,commit)
        ttk.Button(dialog,text=self.tr('apply'),command=choose).pack(pady=8)
