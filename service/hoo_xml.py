import re
from ascript.ios import action

def parse_selector(selector_str):
    """
    解析 Selector 链式调用字符串，返回步骤列表
    支持：child(), parent(n), brother()
    """
    steps = []

    # 去掉 Selector() 前缀
    if selector_str.startswith('Selector()'):
        selector_str = selector_str[10:]

    # 用正则拆分所有的操作：.child(), .parent(n), .brother()
    # 我们手动解析
    i = 0
    current_attrs = {}
    current_tag = None

    while i < len(selector_str):
        # 查找下一个操作符
        if selector_str[i:i+7] == '.child(':
            # 保存当前积累的条件，然后开始新的 child
            if current_tag or current_attrs:
                steps.append({"type": "child", "tag": current_tag, "attrs": current_attrs})
                current_tag = None
                current_attrs = {}
            i += 7
            # 跳过 child() 的内容（应该是空的，后面跟属性）
            if selector_str[i] == ')':
                i += 1
        elif selector_str[i:i+8] == '.parent(':
            # 保存当前积累的条件
            if current_tag or current_attrs:
                steps.append({"type": "child", "tag": current_tag, "attrs": current_attrs})
                current_tag = None
                current_attrs = {}
            i += 8
            # 提取 parent 的参数
            end = selector_str.find(')', i)
            level = int(selector_str[i:end])
            steps.append({"type": "parent", "level": level})
            i = end + 1
        elif selector_str[i:i+10] == '.brother()':
            # 保存当前积累的条件
            if current_tag or current_attrs:
                steps.append({"type": "child", "tag": current_tag, "attrs": current_attrs})
                current_tag = None
                current_attrs = {}
            steps.append({"type": "brother"})
            i += 10
        elif selector_str[i:i+6] == 'type("':
            # 提取 type 的值
            end = selector_str.find('")', i + 6)
            current_tag = selector_str[i+6:end]
            i = end + 2
        elif selector_str[i:i+7] == 'index("':
            end = selector_str.find('")', i + 7)
            current_attrs['index'] = selector_str[i+7:end]
            i = end + 2
        elif selector_str[i:i+6] == 'index(':
            end = selector_str.find(')', i + 6)
            current_attrs['index'] = selector_str[i+6:end]
            i = end + 1
        else:
            # 检查是否是属性方法
            found_attr = False
            for attr in ["enabled", "visible", "accessible", "name", "label", "value"]:
                if selector_str[i:].startswith(f'{attr}('):
                    end = selector_str.find(')', i + len(attr) + 1)
                    val = selector_str[i+len(attr)+1:end]
                    val = val.strip('"')
                    if val in ["True", "False"]:
                        val = val.lower()
                    current_attrs[attr] = val
                    i = end + 1
                    found_attr = True
                    break
            if not found_attr:
                i += 1

    # 添加最后一个积累的条件
    if current_tag or current_attrs:
        steps.append({"type": "child", "tag": current_tag, "attrs": current_attrs})

    return steps

def find_by_steps(root, steps):
    """
    根据步骤查找节点，支持 child、parent 和 brother 操作
    """
    if not steps:
        return None

    # ✅ 第一步：全局搜索（深度优先）
    first_step = steps[0]
    current_nodes = []

    if first_step.get("type") == "child":
        # 递归查找所有匹配的子节点
        def find_all_matching(node, step):
            result = []
            for child in node:
                # tag 过滤
                if step["tag"] and child.tag != step["tag"]:
                    pass
                else:
                    # 属性过滤
                    match = True
                    for k, v in step["attrs"].items():
                        if child.attrib.get(k) != v:
                            match = False
                            break
                    if match:
                        result.append(child)
                # 递归搜索子节点
                result.extend(find_all_matching(child, step))
            return result

        current_nodes = find_all_matching(root, first_step)
        print(f"Step 0: 全局搜索 tag={first_step['tag']}, attrs={first_step['attrs']}")
        print(f"  -> 匹配数量：{len(current_nodes)}")

        if not current_nodes:
            print(f"  -> 返回 None")
            return None

        # 取第一个匹配的节点
        current_nodes = [current_nodes[0]]
        print(f"  -> 选择第 1 个：{current_nodes[0].tag}")

    # 后续步骤
    for step_idx, step in enumerate(steps[1:], start=1):
        next_nodes = []
        prev_step = steps[step_idx - 1]

        # 如果上一步是 parent 或 brother，当前 step 应该是在当前节点集合上过滤，而不是查找子节点
        filter_current = prev_step.get("type") in ("parent", "brother")

        if step.get("type") == "parent":
            # 向上查找父节点
            level = step.get("level", 1)
            print(f"Step {step_idx}: parent({level})")
            for node in current_nodes:
                parent = node
                for _ in range(level):
                    parent = find_parent(root, parent)
                    if parent is None:
                        break
                if parent is not None:
                    next_nodes.append(parent)
            print(f"  -> 结果数量：{len(next_nodes)}")
            current_nodes = next_nodes
            continue

        if step.get("type") == "brother":
            # 获取兄弟节点（父节点的所有子节点，排除当前节点）
            print(f"Step {step_idx}: brother()")
            for node in current_nodes:
                parent = find_parent(root, node)
                if parent is not None:
                    siblings = [child for child in list(parent) if child != node]
                    next_nodes.extend(siblings)
            print(f"  -> 结果数量：{len(next_nodes)}")
            current_nodes = next_nodes
            continue

        # child 操作
        if filter_current:
            # 在当前节点集合上过滤（不向下查找子节点）
            print(f"Step {step_idx}: filter(tag={step['tag']}, attrs={step['attrs']})")
            for node in current_nodes:
                # tag 过滤
                if step["tag"] and node.tag != step["tag"]:
                    continue

                # 属性过滤
                match = True
                for k, v in step["attrs"].items():
                    if node.attrib.get(k) != v:
                        match = False
                        break

                if match:
                    next_nodes.append(node)
        else:
            # 在子节点中查找
            print(f"Step {step_idx}: child(tag={step['tag']}, attrs={step['attrs']})")
            for node in current_nodes:
                children = list(node)
                print(f"  当前节点的子节点:")
                for c in children:
                    print(f"    - {c.tag}: {c.attrib}")
                for child in children:
                    # tag 过滤
                    if step["tag"] and child.tag != step["tag"]:
                        continue

                    # 属性过滤
                    match = True
                    for k, v in step["attrs"].items():
                        if child.attrib.get(k) != v:
                            match = False
                            break

                    if match:
                        next_nodes.append(child)

        print(f"  -> 匹配数量：{len(next_nodes)}")
        if not next_nodes:
            print(f"  -> 返回 None")
            return None

        # 取第一个
        current_nodes = [next_nodes[0]]
        print(f"  -> 选择第 1 个：{current_nodes[0].tag}")

    return current_nodes[0]


def find_parent(root, target_node):
    """
    查找目标节点的父节点
    """
    if target_node == root:
        return None

    for node in root.iter():
        if target_node in list(node):
            return node
    return None

def find(root,selector_str):
    try:
        steps = parse_selector(selector_str)
        print("=== steps ===")
        print(steps)
        result = find_by_steps(root, steps)
        if result is None:
            return None
        return result.attrib
    except Exception as e:
        print(f"find 错误：{e}")
        return None

def find_all(root, selector_str):
    """
    查找所有匹配的节点，返回列表
    """
    attribs = []
    steps = parse_selector(selector_str)
    if not steps:
        return []

    for node in find_by_steps_all(root, steps):
        attribs.append(node.attrib)
    return attribs


def find_by_steps_all(root, steps):
    """
    根据 steps 查找所有匹配的节点（不应用 index 筛选）
    """
    if not steps:
        return []

    # 第一步：全局搜索
    first_step = steps[0]
    current_nodes = []

    # 递归查找所有匹配的子节点
    def find_all_matching(node, step):
        result = []
        for child in node:
            if step["tag"] and child.tag != step["tag"]:
                pass
            else:
                match = True
                for k, v in step["attrs"].items():
                    if child.attrib.get(k) != v:
                        match = False
                        break
                if match:
                    result.append(child)
            result.extend(find_all_matching(child, step))
        return result

    current_nodes = find_all_matching(root, first_step)

    if not current_nodes:
        return []

    # 后续步骤：使用 child() 语义
    for step_idx, step in enumerate(steps[1:], start=1):
        next_nodes = []

        for node in current_nodes:
            children = list(node)
            for child in children:
                if step["tag"] and child.tag != step["tag"]:
                    continue

                match = True
                for k, v in step["attrs"].items():
                    if child.attrib.get(k) != v:
                        match = False
                        break

                if match:
                    next_nodes.append(child)

        if not next_nodes:
            return []

        current_nodes = next_nodes

    return current_nodes


def check(attrib):
    cx = int(attrib['x']) + int(attrib['width']) / 2
    cy = int(attrib['y']) + int(attrib['height']) / 2
    action.click(cx, cy)