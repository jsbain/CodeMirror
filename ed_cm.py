from RootView import RootView
from KeyboardFrame import KeyboardFrame
from KeyboardFrame import key
from uicontainer import FlowContainer
import ui, os, uidir, json, sys, editor, inspect
from console import hud_alert
from functools import partial

class ed_cm(RootView):
    def __init__(self,filename=None):
        RootView.__init__(self)
        
        #presentmode='fullscreen'
        presentmode='panel'     
        self.flex='WH'
        self.border_color=(1,0,0)
        self.border_width=2
        self.present(presentmode)
        
        def simulateTyping(keyobj, sender):
            w=self.view['webview1']
            w.eval_js('editor.replaceSelection({})'.format(json.dumps(keyobj.val)))
            w.eval_js('editor.focus();')
        key.default = simulateTyping
        # set up keyboard frame
        kb=KeyboardFrame()  
        kb.frame=(0,0,self.width,self.height)
        self.add_subview(kb)
        
        #monkeypatch before initializing kb

        kb.undoaction=partial(self.edundo)
        kb.redoaction=partial(self.edredo)  
        kb.setupkb()
        kb.layout=partial(self.kblayout,kb)
        kb.bg_color=(.8,.8,.8)
        
        #setup ui chrome
        def buttonfactory(name,action):
            b=ui.Button(frame=(0,0,75,35),flex='',bg_color='ltgrey')
            b.border_color='grey'
            b.border_width=1
            b.corner_radius=10
            b.title=name.title()
            b.name = name
            b.action=action
            return b
        f=FlowContainer(frame=kb.content.frame,flex='')
        b1=buttonfactory('open',self.edopen)
        b2=buttonfactory('save',self.edsave)
        b3=buttonfactory('select',self.edselect)

        t_filename=ui.TextField(frame=(0,0,kb.content.width-300,35),
                            flex='w',bg_color=(1,1,1),name='filename')
        t_filename.alignment=ui.ALIGN_RIGHT

        w = ui.WebView(name='webview1',
                                 frame=(0,0,kb.content.width,kb.content.height-5),
                                 flex='wh')
        f.add_subview([b1,b2,b3,t_filename,w])
        f.flex='w'
        kb.add_content(f)
        self.view=f
        self.kb=kb
        self.w=w
        self.initView(filename)
        
    def edundo(self,kb):
        w=self.view['webview1']
        w.eval_js('editor.undo();')
    def edredo(self,kb):
        w=self.view['webview1']
        w.eval_js('editor.redo();')
 
    # webview delegate methods
    def webview_should_start_load(w, url, nav_type):
        # url scheme... uri == command
        return True
    def webview_did_start_load(webview):
        pass
    def webview_did_finish_load(webview):
        pass
    def webview_did_fail_load(webview, error_code, error_msg):
        pass

    def refreshsize(self):
        pass
        try:
            w=self.w
            #w.eval_js('resizeEditor();')
            pass
        except AttributeError:
            pass

    def kblayout(self,kb):
        #allow kb to resizs, then resize editor
        ui.cancel_delays()
        KeyboardFrame.layout(kb)
        #ui.delay(self.refreshsize,0.75)
        
    #
    def gotoLine(self,line):
        w=self.view['webview1']
        w.eval_js('editor.setCursor({},0);'.format(line))
    def edopen(self,sender):
        '''open the file named in the textbox, load into editor'''
        w=self.view['webview1']
        f=self.view['filename']
        try:
            with open(f.text) as file:
                w.eval_js('editor.setValue({});'.format(json.dumps(file.read())))
                hud_alert('opened '+os.path.relpath(file.name))
                w.eval_js('editor.setOption("mode","{}");'.format(self.determine_style(file.name)))
                
                w.eval_js('CodeMirror.autoLoadMode(editor, "{}");'.format(self.determine_style(file.name)))
                #w.eval_js('editor.focus();')
        except (IOError):
            hud_alert( 'file not found')

    def edsave(self,sender):
        '''save the editor content to file in filename textbox'''
        w=self.view['webview1']
        f=self.view['filename']
        try:
            with open(f.text,'w') as file:
                file.write(w.eval_js('editor.getValue();'))
                hud_alert('saved '+os.path.relpath(file.name))
        except(IOError):
            hud_alert('could not save')

    def edselect(self,sender):
        '''display file selection dialog, and set filename textfield'''
        w=self.view['webview1']
        f=self.view['filename']
        def setter(s):
            f.text=os.path.relpath(s)
        uidir.getFile(setter)

    @classmethod
    def determine_style(self,filename):
        '''return style name used by change_syntax, based on file extension.  '''
        syntaxes={'css':'css',
                 'html':'htmlmixed',
                 'js':'javascript',
                 'php':'php',
                 'py':'python',
                 'vb':'vb',
                 'xml':'xml',
                 'c':'c',
                 'cpp':'cpp',
                 'sql':'sql',
                 'bas':'basic',
                 'pas':'pas',
                 'pl':'perl',
                 'md':'markdown'}
        try:
            ext=os.path.splitext(filename)[1][1:]
            syntax=syntaxes[ext]
            #print ext
        except(KeyError):
            #print ext
            syntax='robotstxt'
        return syntax

    def initView(self,filename=None):
        '''setup the webview.  if filename is omitted, open current file in editor'''
        #find path of this script, to find abs path of html file
        self.st=inspect.stack()
        self.sys=sys
        p= os.path.dirname([st[1] for st in self.st if st[3]=='initView'][0])
        s= os.path.join(p,os.path.splitext(__file__)[0])

        srcname='demo/ed_cm.html'
        w=self.w
        w.load_url(os.path.join(p,srcname))
        hud_alert('wait',duration=1.0)
        ui.delay(lambda:w.eval_js('resizeEditor()'),0.25)
        w.delegate = self

        if filename is not None:
            f=self.view['filename']
            try:
                f.text=filename
                ui.delay(partial( self.edopen,w), 0.5)
            except:
                pass
        

    def openfile(self,filename):
        if filename is not None:
            f=self.view['filename']
            try:
                f.text=filename
                ui.delay(partial( self.edopen,self.view['open']), 1)
            except:
                pass
if __name__=='__main__':
    e=ed_cm(editor.get_path()) 
    #e=ed_cm()
