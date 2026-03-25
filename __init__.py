###license[GNU General Public License v3.0 or later]
# Copyright (C) 2026  [o_oo_gote510]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
###

#======Math Controller addon======#
#===========MC_0.4.5=================#
import bpy
from bpy.app.translations import pgettext_iface
import traceback
import ast


#astパーサー用
# For AST parser
MATH_OPS = {ast.Add: 'ADD', ast.Sub: 'SUBTRACT', ast.Mult: 'MULTIPLY', ast.Div: 'DIVIDE', ast.Pow: "POWER"}
FUNC_OPS = {
    # --- Functions ---
    'add': 'ADD',
    'sub': 'SUBTRACT',
    'mul': 'MULTIPLY',
    'div': 'DIVIDE',
    'madd': 'MULTIPLY_ADD',
    'pow': 'POWER',
    'log': 'LOGARITHM',
    'sqrt': 'SQRT',
    'inv_sqrt': 'INVERSE_SQRT',
    'abs': 'ABSOLUTE',
    'exp': 'EXPONENT',

    # --- Comparison ---
    'min': 'MINIMUM',
    'max': 'MAXIMUM',
    'less': 'LESS_THAN',
    'greater': 'GREATER_THAN',
    'sign': 'SIGN',
    'compare': 'COMPARE',
    's_min': 'SMOOTH_MIN',
    's_max': 'SMOOTH_MAX',

    # --- Rounding ---
    'round': 'ROUND',
    'floor': 'FLOOR',
    'ceil': 'CEIL',
    'trunc': 'TRUNCATE',
    'fract': 'FRACTION',
    'mod_t': 'TRUNCATED_MODULO',
    'mod_f': 'FLOORED_MODULO',
    'wrap': 'WRAP',
    'snap': 'SNAP',
    'pingpong': 'PINGPONG',

    # --- Trigonometric ---
    'sin': 'SINE',           
    'cos': 'COSINE',        
    'tan': 'TANGENT',       
    'asin': 'ARCSINE',
    'acos': 'ARCCOSINE',
    'atan': 'ARCTANGENT',
    'atan2': 'ARCTAN2',
    'sinh': 'SINH',
    'cosh': 'COSH',
    'tanh': 'TANH',

    # --- Conversion ---
    'rad': 'RADIANS',
    'deg': 'DEGREES',
}
#ダイアログ用
# For dialog
HELP_LAYOUT_DATA = {
    "Functions": [
        ('+    add(  ,  )', 'Add'), 
        ('-    sub(  ,  )', 'Subtract'), 
        ('*    mul(  ,  )','Multipy'),
        ('/    div(  ,  )', 'Divide'), 
        ('madd(  ,  ,  )', 'Multiply Add'), 
        ('', ''),
        ('log(  ,  )', 'Logarithm'), 
        ('sqrt(  )', 'Square Root'), 
        ('inv_sqrt(  )', 'Inverse Square Root'),
        ('abs(  )', 'Absolute'), 
        ('exp(  )', 'Exponent')
    ],
    "Comparison": [
        ('min(  ,  )', 'Minimum'), 
        ('max(  ,  )', 'Maximum'), 
        ('less(  ,  )', 'Less Than'),
        ('greater(  ,  )', 'Greater Than'), 
        ('sign(  )', 'Sign'), 
        ('compare(  ,  ,  )', 'Compare'),
        ('s_min(  ,  ,  )', 'Smooth Minimum'), 
        ('s_max(  ,  ,  )', 'Smooth Maximum')
    ],
    "Rounding": [
        ('round(  )', 'Round'), 
        ('floor(  )', 'Floor'), 
        ('ceil(  )', 'Ceil'),
        ('trunc(  )', 'Truncate'), 
        ('', ''),
        ('fract(  )', 'Fraction'), 
        ('mod_t(  ,  )', 'Modulo'),
        ('mod_f(  ,  )', 'Floored Modulo'), 
        ('wrap(  ,  ,  )', 'Wrap'), 
        ('snap(  ,  )', 'Snap'),
        ('pingpong(  ,  )', 'Ping-Pong')
    ],
    "Trigonometric": [
        ('sin(  )', 'Sine'), 
        ('cos(  )', 'Cosine'), 
        ('tan(  )', 'Tangent'),
        ('', ''),
        ('asin(  )', 'Arcsine'), 
        ('acos(  )', 'Arccosine'), 
        ('atan(  )', 'Arctangent'),
        ('atan2(  ,  )', 'Arctan2'),
        ('', ''), 
        ('sinh(  )', 'Hyperbolic Sine'), 
        ('cosh(  )', 'Hyperbolic Cosine'), 
        ('tanh(  )', 'Hyperbolic Tangent')
    ],
    "Conversion": [
        ('rad(  )', 'To Radians'), 
        ('deg(  )', 'To Degrees')
    ]
}


change_list_formula = [["^","**"]]

# --- プロパティグループのクラス群 ---
# --- Property group classes ---
class o_oo_FormulaItem(bpy.types.PropertyGroup):
    
    def get_parent_node(self):
        parent_nodes = self.id_data.nodes
        parent_node = parent_nodes.get(self.get("parent_node_name", ""))
        #親ノードの喪失の保険
        # Fallback in case the parent node is lost
        if not parent_node or not hasattr(parent_node, "formulas") or self not in parent_node.formulas.values():#
            for n in parent_nodes:
                if hasattr(n, "formulas") and any(i == self for i in n.formulas):
                    self["parent_node_name"] = n.name
                    return n
                else:
                    None
        return parent_node

    # カスタムグループノードのupdate関数を起動させる。
    # Trigger the update function of the custom group node
    def update_in_FromulaItem(self, context):
        parent_node = self.get_parent_node() 
        if parent_node and hasattr(parent_node, "update_in_MathController"):
            parent_node.update_in_MathController(self)
            
    # f1=,[入力欄] :{name}={expression} 
    # f1=,[input field] :{name}={expression}
    num: bpy.props.IntProperty(name="Num")
    name: bpy.props.StringProperty(name="Name")
    expression: bpy.props.StringProperty(name="Formula", default="", update=update_in_FromulaItem)
    last_formula: bpy.props.StringProperty(name="Last_Formula",default="")
    
    def id_property_register(self):
        self["input_sockets"] = list()
        self["error_msg"] = ""
        self["scale"]=[0,0]
        self["parent_node_name"]= ""    

class o_oo_NODE_OT_FormulaAdd(bpy.types.Operator):
    bl_idname = "o_oo.formula_add"
    bl_label = "Add"
    def execute(self, context):
        
        parent_node = getattr(context, "node", None) or context.active_node
        #print(f"parent_node{parent_node}")#deb
        new_idx = len(parent_node.formulas) + 1
        item = parent_node.formulas.add()
        item.num = new_idx
        item.name = f"f{new_idx}"
        item.id_property_register()
        item["parent_node_name"]=parent_node.name

        return {'FINISHED'}

class o_oo_NODE_OT_FormulaRemoveStrict(bpy.types.Operator):
    bl_idname = "o_oo.formula_remove_strict"
    bl_label = "Remove"
    def execute(self, context):
        node = getattr(context, "node", None) or context.active_node
        if len(node.formulas) <= 1: # f1は削除させない
            # Do not allow deletion of f1
            return {'CANCELLED'}
        last_item = node.formulas[-1]
        if last_item.expression != "":
            self.report({'WARNING'}, "Clear the formula first.")
            return {'CANCELLED'}
        node.formulas.remove(len(node.formulas) - 1)
        return {'FINISHED'}
# --- ダイアログ用のクラス群 ---
# --- Dialog classes ---
class o_oo_NODE_OT_FormulaEditor(bpy.types.Operator):
    bl_idname = "o_oo.formula_editor"
    bl_label = "Advanced Formula Editor"
    bl_options = {'REGISTER', 'UNDO'}
    index: bpy.props.IntProperty()
    node_name: bpy.props.StringProperty()
    text_input: bpy.props.StringProperty(name="")

    def execute(self, context):  
        # 親ノードの喪失の保険
        # Fallback in case the parent node is lost
        if not self.node:
           tree = context.space_data.edit_tree
           if not tree: return {'CANCELLED'}
           self.node = tree.nodes.get(self.node_name)

        if getattr(self,"node",""):
            self.node.formulas[self.index].expression = self.text_input
            return {'FINISHED'}
        return {'CANCELLED'}
    
    def invoke(self, context, event):

        if not getattr(self,"node",""):
            #print("No:getattr for context")#deb
            self.node = getattr(context, "node", None) or context.active_node
        self.node_name = self.node.name  # ノード名を保存
        # Save node name
        self.text_input = self.node.formulas[self.index].expression
        # ダイアログの幅を調整
        # Adjust dialog width(len=100 : width=1000 per 100)
        d_width=(len(self.text_input)//10)*100
        d_width = 1000 if d_width < 1000 else d_width if d_width < 10000 else 10000
        return context.window_manager.invoke_props_dialog(self, width=int(d_width))
    
    def draw_recursive(self, layout, func_node):
        if isinstance(func_node, list):
            row = layout.row(align=True)
            row.alignment = "LEFT"
            for item in func_node:
                if isinstance(item, list):
                    col=row.column(align=True)
                    col.alignment="LEFT"
                    col.label(text="")
                    self.draw_recursive(col, item)
                elif isinstance(item, str):
                    row.label(text=str(item))
        else:
            pass

    def draw(self, context):
        layout = self.layout
        # ラベルなしでプロパティを表示し、横幅いっぱいに広げる
        # Display property without label and expand to full width
        row = layout.row()
        row.prop(self, "text_input", text="")
        
        box = layout.box()
        a=o_oo_FormulaParser(self.text_input)
        funcs=a.parse()
        self.draw_recursive(box, funcs)
        
        box2=layout.box()
        Hrow = box2.row(align=True)
        
        for category, items in HELP_LAYOUT_DATA.items():
            Hcol = Hrow.column(align=True)
            Hcol.alignment="LEFT"
            # カテゴリの見出し
            # Category header
            category_inte=pgettext_iface(category, "NodeTree")
            Hcol.label(text=category_inte)
            Hcol.label(text="─"*17)
            Hrow2=Hcol.row(align=True)
            Hrow2.alignment="LEFT"
            Hcol1=Hrow2.column(align=True)
            Hcol2=Hrow2.column(align=True)
            Hcol1.alignment="LEFT"
            Hcol2.alignment="LEFT"
            
            for symbol, desc in items:
                if symbol and desc:
                    desc_inte=pgettext_iface(desc, "NodeTree")
                    Hcol1.label(text=desc_inte)
                    Hcol2.label(text=symbol)
                else:
                    Hcol1.label(text="─"*10)
                    Hcol2.label(text="─"*7)

class o_oo_FormulaParser:
    #(,)で深まる木構造生成パーサ
    # Parser that generates a tree structure deepening with parentheses (,)
    def __init__(self, formula):
        self.formula = formula
        self.pos = 0
        self.pos2 = 0

    def parse(self):
        result = []
        try:
          while self.pos < len(self.formula):
              char = self.formula[self.pos]
              if char == ')':
                  self.pos2 += -1
                  if self.pos2 >=0:
                      return result
                  else:
                      self.pos2=0
              if not result:
                  result.append(char)
              else:
                  result[-1] += char
              self.pos += 1
              if char == '(':
                  self.pos2 += 1
                  result.append(self.parse())
                  char = self.formula[self.pos]
                  result.append(char)
                  self.pos += 1
        finally:
          return result
# --- サブグループノード用のクラス群 --- 
# --- Sub-group node classes ---
class o_oo_NODE_OT_ExpandFormulaGroup(bpy.types.Operator):
    bl_idname = "o_oo.expand_formula_group"
    bl_label = "Expand to Group Node"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        parent_tree = context.space_data.edit_tree
        parent_node=getattr(context, "node", None) or context.active_node
        
        if not (parent_tree and parent_node):
            return {'CANCELLED'}
        group_node = parent_tree.nodes.new(type=parent_node.group_type)
        group_node.node_tree = parent_node.node_tree
        
        # 生成位置を一旦、元のノードと同じにする（この後マウスに重なるため）
        # Temporarily set the generated position to the same as the original node (it will overlap the mouse afterward)
        group_node.location = parent_node.location
        
        # 選択状態を新しいノードに限定する
        # Restrict selection to the new node
        bpy.ops.node.select_all(action='DESELECT')
        group_node.select = True
        parent_tree.nodes.active = group_node
        
        # マウス移動（グラブ）モードを開始する
        # Start mouse move (grab) mode
        bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
        return {'FINISHED'}

# --- 数式ノード生成用のクラス群 ---
# --- Classes for formula node generation ---
class o_oo_NodeBuilder:
    def __init__(self, controller, tree):
        self.c = controller
        self.tree = tree
        self.links = tree.links
        self.node_in = None
        self.node_out = None
        self.anchor_name=self.c.formula_id
        self.node_dimension=[]

    def get_or_create_frame(self):
        frame_name=f"Frame_{self.anchor_name}"
        frame = self.tree.nodes.get(frame_name)
        if not frame:
            frame=self.tree.nodes.new("NodeFrame")
            frame.name=frame_name
            frame.label=f"Formula:{self.anchor_name}"
        self.frame=frame
        return
    
    def clear_frame_contents(self,frame):
        for node in list(self.tree.nodes):
            if node.parent == frame and node.bl_idname !="NodeReroute":
                self.tree.nodes.remove(node)

    def get_or_create_reroute(self,frame):
        reroute_name = f"Anchor_{self.anchor_name}"
        reroute = self.tree.nodes.get(reroute_name)
        if not reroute:
            reroute = self.tree.nodes.new("NodeReroute")
            reroute.name=reroute_name
            reroute.location=(200,-20*self.c.formula_num)
        self.reroute=reroute
        return
    
    def renew(self, now: set, new: set):
        return now - new, new - now

    def setup_interface(self, all_vars):
        last_vars=set()
        for i, item in enumerate(self.c.formulas):
            if i != self.c.formula_num:
                last_vars |= set(item["input_sockets"])

        remo, make = self.renew(
        { item.name for item in self.tree.interface.items_tree 
        if item.in_out == "INPUT"
        },
         last_vars|all_vars
        )
        
        
        # 新規ソケット追加
        # Add new sockets
        makesockets = sorted(list(make))
        for newsocket in makesockets:
            self.tree.interface.new_socket(name=newsocket, in_out='INPUT', socket_type='NodeSocketFloat')
        
        
        # 出力ソケット (f{}) チェック
        # Output socket (f{}) check
        socket = next((item for item in self.tree.interface.items_tree 
               if item.name == self.anchor_name and item.in_out == 'OUTPUT'), None)
        
        if not socket:
            socket=self.tree.interface.new_socket(name=self.anchor_name, in_out='OUTPUT', socket_type='NodeSocketFloat')
        self.c.forms["input_sockets"]=list(all_vars)
        my_num=self.tree.interface.items_tree.find(socket.name)
        for i in range(my_num):
            item=self.tree.interface.items_tree[i]
            oth_num = self.tree.interface.items_tree.find(item.name)
            if item.in_out=="OUTPUT":
                if int(socket.name[1:]) < int(item.name[1:]):
                    my_num += -1
        self.tree.interface.move(socket,my_num)
        
        # 不要ソケット削除
        # Remove unnecessary sockets
        output_rema={i.name for i in self.c.formulas if i.expression }
        for item in list(self.tree.interface.items_tree):
            if (item.item_type == 'SOCKET' and item.in_out == 'INPUT' and item.name in remo):
                #print("item.name",item.name)#deb
                #print("socket",self.c.inputs.get(item.name,"no").is_linked)
                if not getattr(self.c.inputs.get(item.name,"no"),"is_linked",""):
                    self.tree.interface.remove(item)
        #!警告:ソケットに関して、INPUTとOUTPUTの取得削除をおなじfor構文の中で行うと、blenderがクラッシュした。
        #!Warning: Performing retrieval and deletion of INPUT and OUTPUT sockets in the same for loop caused Blender to crash.
        for item in list(self.tree.interface.items_tree):
            if (item.item_type == 'SOCKET' and item.in_out == 'OUTPUT' and item.name not in output_rema):
                if not getattr(self.c.inputs.get(item.name,"no"),"is_linked",""):
                    self.tree.interface.remove(item)

    def dig_unary(self,ast_node,i):

        """連続した符号をまとめる"""
        """Combine consecutive unary signs"""

        if isinstance(ast_node, ast.UnaryOp):
            # ast.USub-> i=-i
            if isinstance(ast_node.op, ast.USub):
                i = -i
            # ast.UAdd-> i=i
            if isinstance(ast_node.operand, ast.UnaryOp):
                return self.dig_unary(ast_node.operand, i) # ← ast_node ではなく .operand を渡す
                # Pass .operand instead of ast_node
            else:
                return ast_node.operand, i
            
        return ast_node ,0

    def build_node(self, ast_node, depth):
            
        """再帰的なノード構築"""
        """Recursive node construction"""

        if isinstance(ast_node, ast.Constant):
            return ast_node.value
        elif isinstance(ast_node, ast.Name):
            if ast_node.id[0]=="f" and (ast_node.id[1:]).isdigit():
                reroute = self.tree.nodes.get("Anchor_"+ast_node.id,None)
                if reroute: 
                    return reroute
                else:
                    self.c.forms["error_msg"]="Unavailable function symbol"
                    return 0
            else:
                return ast_node.id
        if isinstance(ast_node,(ast.BinOp,ast.Call)):
            
            depth +=1
            if depth > ( len(self.node_dimension)-1 ):
                self.node_dimension.append(-1)
            self.node_dimension[depth]+=1
            
            math_node = self.tree.nodes.new("ShaderNodeMath")
            math_node.location = (-200*depth, -180*self.node_dimension[depth])


            if isinstance(ast_node, ast.BinOp):
                left = self.build_node(ast_node.left, depth)
                right = self.build_node(ast_node.right, depth)
                
                try:
                    math_node.operation = MATH_OPS.get(type(ast_node.op), '')
                    for i, val in enumerate([left, right]):
                        if isinstance(val, (int, float)):
                            math_node.inputs[i].default_value = val
                        elif isinstance(val, str):
                            self.links.new(self.node_in.outputs[val], math_node.inputs[i])
                        else:
                            self.links.new(val.outputs[0], math_node.inputs[i])
                except:
                    self.c.forms["error_msg"]="maybe: unavailable symbol"
                    
            elif isinstance(ast_node, ast.Call):
                math_node.operation = FUNC_OPS.get(ast_node.func.id, 'ADD')
                args = []
                for h, arg in enumerate(ast_node.args):
                    args.append(self.build_node(arg, depth))
                for i, val in enumerate(args):
                    try:
                        if isinstance(val, (int, float)):
                            math_node.inputs[i].default_value = val
                        elif isinstance(val, str):
                            self.links.new(self.node_in.outputs[val], math_node.inputs[i])
                        else:
                            self.links.new(val.outputs[0], math_node.inputs[i])
                    except:
                        self.c.forms["error_msg"]="function:"+ast_node.func.id
                        self.c.forms["error_msg"]=self.c.forms["error_msg"]+",maybe:"+"too many vars"
                        print("func error")
            math_node.parent=self.frame
            return math_node
        
        elif isinstance(ast_node, ast.UnaryOp):
            new_ast, i = self.dig_unary(ast_node, 1)
            if i == 1:
                return self.build_node(new_ast, depth)
            elif isinstance(new_ast, ast.Constant):
                return -self.build_node(new_ast, depth)
            else:
                new_node = ast.BinOp(
                    left=ast.Constant(value=-1),
                    op=ast.Mult(),
                    right=new_ast
                )
                ast.fix_missing_locations(new_node)
                return self.build_node(new_node, depth)        

    def run(self, node_ast, all_vars):
        """構築プロセスの実行フロー"""
        """Execution flow of the build process"""
        """Frameベースの構築フロー"""
        """Frame-based build flow"""
        # 1. 準備
        # 1. Preparation
        self.get_or_create_frame()
        self.clear_frame_contents(self.frame)
        self.frame.shrink = False
        self.get_or_create_reroute(self.frame)
        # 2. ソケット更新
        # 2. Socket update
        self.setup_interface(all_vars)
        self.tree.nodes.remove(self.frame)
        if node_ast:#empty_filter
            self.get_or_create_frame()

        # 3. 入出力ノードの確保
        # 3. Ensure input/output nodes
        self.node_in = next((n for n in self.tree.nodes if n.bl_idname == "NodeGroupInput"), None)
        if not self.node_in:
            self.node_in = self.tree.nodes.new("NodeGroupInput")
            self.node_in.location = (-300, 0)

        self.node_out = next((n for n in self.tree.nodes if n.bl_idname == "NodeGroupOutput"), None)
        if not self.node_out:
            self.node_out = self.tree.nodes.new("NodeGroupOutput")
            self.node_out.location = (300, 0)
        # 4. ノード構築と最終接続の設定
        # 4. Build nodes and set final connections
        if node_ast:#empty_filter
            final_node = self.build_node(node_ast, -1)
            if final_node:
                if isinstance(final_node, (int, float)):
                    self.node_out.inputs[self.anchor_name].default_value = final_node
                elif isinstance(final_node, str):#!erorr:use too long value name
                    self.links.new(self.node_in.outputs[final_node], self.reroute.inputs[0])
                else:
                    self.links.new(final_node.outputs[0], self.reroute.inputs[0])
        
        
            self.links.new(self.reroute.outputs[0], self.node_out.inputs[self.c.formula_id])
        else:
  
            pass#!警告:frameが削除された後、再生成される前に呼び出すと、blenderがクラッシュした。
            #!Warning: Calling this after the frame is deleted and before it is recreated caused Blender to crash.
        #タイマーで、勝利終了後に正確にノード整理を行う。
        # Use a timer to properly arrange nodes after completion
        bpy.app.timers.register(lambda: o_oo_delayed_positioning(self), first_interval=0.01)

def o_oo_delayed_positioning(builder):
    try:
        # すべての描画・計算が完了した後に実行される
        # Executed after all drawing and calculations are completed
        b=builder
        
        farthest = 300
        scale_x=0
        scale_y=0

        for n in b.tree.nodes:
            if farthest > n.location[0] and n.bl_idname != "NodeGroupInput":
                farthest = n.location[0]
            if scale_x < abs(n.location[0]) and n.parent==b.frame:
                scale_x = abs(n.location[0])
            if scale_y < abs(n.location[1]) and n.parent==b.frame:
                scale_y = abs(n.location[1])
        b.node_in.location = (farthest - 200, 0)
        k=0

        b.c.forms["scale"]=[scale_x,scale_y]
        for i in b.c.formulas:
            if i.expression:
                (b.tree.nodes.get(f"Frame_{i.name}")).location.y=k                
                k += - i["scale"][1] -200

    finally:
        return None 

# --- カスタムグループノード本体 ---
# --- Custom group node main body ---
def o_oo_delay_copy(new,old):
    try:

        if old.node_tree:
            new.node_tree = old.node_tree.copy()
        else:
            new_tree = bpy.data.node_groups.new(".FormulaTree",new.node_type)
            new.node_tree = new_tree
        new.node_tree.name = ".internal_copy"
    
    
    finally:return None

class o_oo_BaseMathController(bpy.types.NodeCustomGroup):

    bl_label = "Math Controller"
    bl_icon = 'NODE'
    bl_tree_type = 'GeometryNodeTree'

    formulas: bpy.props.CollectionProperty(type=o_oo_FormulaItem)

#====================init & copy:内部ツリー生成・update_in_MathController呼び出し============#
#====================init & copy: internal tree generation & calling update_in_MathController============#
    def init(self, context):
        new_tree = bpy.data.node_groups.new(".internal", self.bl_tree_type)
        self.node_tree = new_tree
        self.width = 240
        # 初期状態で f1 を作成
        # Create f1 in the initial state
        if len(self.formulas) == 0:
            item = self.formulas.add()
            item.num=1
            item.name = "f1"
            item.id_property_register()
            item["parent_node_name"]=self.name
            
    def copy(self, node):
        # 3. タイマーを登録して、0.01秒後に復元処理を予約
        # Register a timer to schedule restoration after 0.01 seconds
        #これより、ctrl+shift+Dでのリンクあり複製の際のリンク切れを防ぐ。
        # This prevents link breakage when duplicating with Ctrl+Shift+D
        #!警告:ctrl+shift+Dを、タイマーなし且つ内部ノード非継承(完全な新規ノードと交換)という条件で行うとクラッシュした。
        #!Warning: Performing Ctrl+Shift+D without a timer and without inheriting internal nodes (fully replacing with a new node) caused a crash.
        #また、ctrl+shift+Dでタイマーなしあるいは処理が終わらない時に、条件{ 内部ノード継承(.copy())やその他の参照行為 }が行われるとリンクが切れるにとどまるが成功しない。
        # Also, without a timer or if processing is incomplete, operations like inheriting internal nodes (.copy()) or other references result in broken links and failure.
        bpy.app.timers.register(
            lambda: o_oo_delay_copy(self,node),
            first_interval=0.01
        )
        

#============================draw_buttons:常時実行(formula,link,ボタン表示)===#
#============================draw_buttons: always executed (formula, link, button display)===#
    def draw_buttons(self, context, layout):
        
        main_col = layout.column(align=True)
        
        # ボタンエリア
        # Button area
        btn_row = main_col.row(align=True)
        btn_row.alignment = 'RIGHT'
        btn_row.operator("o_oo.formula_add", icon='ADD', text="")
        btn_row.operator("o_oo.formula_remove_strict", icon='REMOVE', text="")
        # 数式フォームエリア
        # Formula form area
        for i, item in enumerate(self.formulas):
            row = main_col.row(align=True)
            
            # IDラベル
            # ID label
            sub = row.row(align=True)
            sub.alignment = 'LEFT'#<- very very important
            sub.label(text=f"{item.name} =")
         
            # 入力欄
            # Input field
            row.prop(item, "expression", text="")
            
            op = row.operator("o_oo.formula_editor", icon='TEXT', text="")
            if op:
                op.index = i
            error = item.get("error_msg","")
            if error:
                # alert=Trueにすると、中のボタンやラベルが自動的に警告色になる
                # Setting alert=True makes buttons and labels display warning colors automatically
                box = main_col.box()
                box.alert = True
                box.label(text=error, icon='ERROR')
        sub_row=main_col.row(align=True)
        sub_col=sub_row.column(align=True)
        if self.node_tree:
            sub_row.label(text=f"Linked: {self.node_tree.name}", icon='LINKED')
            op=sub_row.operator("o_oo.expand_formula_group", text="", icon='NODETREE')
        else:
            print("lost node_tree")#deb
#==========================update_in_MathController:入力検査->rebuild_internal呼び出し=======#
#==========================update_in_MathController: input validation -> call rebuild_internal=======#
    def update_in_MathController(self,forms):
        self.forms=forms
        self.formula=forms.expression
        self.formula_id=forms.name
        self.formula_num=int(self.formula_id[1:])-1
        self.last_formula=forms.last_formula
        #print("update_in_MathController_start")#deb
        try:

            if self.last_formula == self.formula:
                print("update_in_MathController_end[1]")
                return
            if self.get("_rebuilding", False):
                print("update_in_MathController_end[2]")
                return
            if not self.node_tree:
                print("Error: Node tree is missing.")
                return
            
            self._rebuilding = True
            try:
                self.forms["error_msg"]=""         
                self.rebuild_internal(self.node_tree)
                self.last_formula=self.formula
                self.formulas[self.formula_num].last_formula=self.last_formula
            finally:
                self._rebuilding = False               
        except Exception as e:
            self.forms["error_msg"]="unklnown error"
            print("Error in update_in_MathController:")
            traceback.print_exc()

#========================================rebuild_internal:数式ノード生成======#
#========================================rebuild_internal: generate formula nodes======#
    def rebuild_internal(self, tree):
        # 数式の下準備
        # Preprocessing of the formula
        formula_nor = self.formula
        for old, new in change_list_formula:
            formula_nor = formula_nor.replace(old, new)
        
        try:
            if self.formula != "":#empty_filter
                node_ast = ast.parse(formula_nor, mode='eval').body
                funcs = {n.func.id for n in ast.walk(node_ast) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
                all_vars = {n.id for n in ast.walk(node_ast) if isinstance(n, ast.Name) and n.id not in funcs}
                all_vars = {i for i in all_vars if not (i[0]=="f" and (i[1:]).isdigit())}
            else:
                node_ast=""
                all_vars=set()
        except Exception as e:
            traceback.print_exc()
            print("Invalid Formula")
            self.forms["error_msg"]="Invalid Formula"
            return
        
        if any(len(i)>60 for i in all_vars):#to avoid key miss
            self.forms["error_msg"]="maybe: Variable name too long (max 60 chars)"
            return
        # Builderを生成し、一括実行
        # Create builder and execute in batch
        #builderで許可するノードタイプに限って分析する
        # Analyze only node types allowed by the builder
        builder = o_oo_NodeBuilder(self, tree)
        builder.run(node_ast, all_vars)

    def free(self):
        if self.node_tree and self.node_tree.users <= 2:#!
            bpy.data.node_groups.remove(self.node_tree)
            
class o_oo_SHADER_NodeMathController(bpy.types.ShaderNodeCustomGroup, o_oo_BaseMathController):
    bl_idname = "o_oo.ShaderNodeMathController"
    bl_tree_type = 'ShaderNodeTree'
    group_type='ShaderNodeGroup'
    def init(self,context):
        super().init(context)

class o_oo_COMP_NodeMathController(bpy.types.CompositorNodeCustomGroup, o_oo_BaseMathController):
    bl_idname = "o_oo.CompositorNodeMathController"
    bl_tree_type = 'CompositorNodeTree'
    group_type='CompositorNodeGroup'
    def init(self,context):
        super().init(context)

class o_oo_GEO_NodeMathController(bpy.types.GeometryNodeCustomGroup, o_oo_BaseMathController):
    bl_idname = "o_oo.GeometryNodeMathController"
    bl_tree_type = 'GeometryNodeTree'
    group_type='GeometryNodeGroup'
    def init(self,context):
        super().init(context)

# --- 登録用の関数群 ---
# --- Registration functions ---
classes = (
    o_oo_FormulaItem,
    o_oo_NODE_OT_FormulaAdd,
    o_oo_NODE_OT_FormulaRemoveStrict,
    o_oo_NODE_OT_FormulaEditor,
    o_oo_NODE_OT_ExpandFormulaGroup,
    o_oo_BaseMathController,
    o_oo_SHADER_NodeMathController,
    o_oo_GEO_NodeMathController,
    o_oo_COMP_NodeMathController,
)


def o_oo_menu_func_geo(self, context):
    op = self.layout.operator("node.add_node", text="Math Controller")
    op.type = "o_oo.GeometryNodeMathController"

def o_oo_menu_func_shader(self, context):
    op = self.layout.operator("node.add_node", text="Math Controller")
    op.type = "o_oo.ShaderNodeMathController"

def o_oo_menu_func_comp(self, context):
    op = self.layout.operator("node.add_node", text="Math Controller")
    op.type = "o_oo.CompositorNodeMathController"
    
def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.types.NODE_MT_category_GEO_UTILITIES.append(o_oo_menu_func_geo)
    bpy.types.NODE_MT_category_shader_utilities.append(o_oo_menu_func_shader)
    bpy.types.NODE_MT_category_compositor_utilities.append(o_oo_menu_func_comp)



def unregister():
    # メニューから削除（登録時と同じ関数を指定する）
    # Remove from menu (specify the same function as used during registration)
    bpy.types.NODE_MT_category_GEO_UTILITIES.remove(o_oo_menu_func_geo)
    bpy.types.NODE_MT_category_shader_utilities.remove(o_oo_menu_func_shader)
    bpy.types.NODE_MT_category_compositor_utilities.remove(o_oo_menu_func_comp)
    
    # クラスを「逆順」で削除
    # Unregister classes in reverse order
    for i,cls in enumerate(reversed(classes)):
        try:
            bpy.utils.unregister_class(cls)
            print(f"[{i}]:done")
        except:
            print(f"[{i}]:couldn't")
            
if __name__ == "__main__":
    register()
