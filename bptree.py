import json
import csv
import math
import argparse
import sys

class data:
    def save(path: str, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def load(path: str):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
        
class Bptree:
    def __init__(self, datafile):
        self.index = datafile
        self.n = int(self.index["n"])

    def get_nid(self):
        nid = str(self.index["next_nid"])
        self.index["next_nid"] += 1
        return nid
    
    def get_node(self, nid):
        return self.index["nodes"][str(nid)]

    def put_node(self, nid, node):
        node["m"] = len(node["p"])
        self.index["nodes"][str(nid)] = node

    def get_rootid(self):
        return str(self.index["root"])

    def set_rootid(self, nid):
        self.index["root"] = int(nid)

    def choose_child(self, key, node):
        for pair in node["p"]:
            if key < pair["key"]:
                return str(pair["left_child_node"])
        return str(node["r"])

    def find_leaf_node(self, key):
        nodeList = []
        nid = self.get_rootid()
        node = self.get_node(nid)
        while(node["is_leaf"] == False):
            nodeList.append(nid)
            nid = self.choose_child(key, node)
            node = self.get_node(nid)
        return nid, nodeList

    def insert(self, key, val):
        leafNid, nidList = self.find_leaf_node(key)
        leafNode = self.get_node(leafNid)
        for pair in leafNode["p"]:
            if key == pair["key"]:
                return
        idx = 0
        while idx < leafNode["m"] and leafNode["p"][idx]["key"] < key:
            idx += 1
        leafNode["p"].insert(idx, {"key": key, "value": val}) #idx + 1 실수
        self.put_node(leafNid, leafNode)
        if leafNode["m"] >= self.n:
            parentKey, newNid = self.split_leaf(leafNid)
            self.parent_insert(parentKey, nidList, leafNid, newNid)
    
    def split_leaf(self, nid):
        node = self.get_node(nid)
        midIdx = math.ceil(node["m"] / 2)
        newNid = self.get_nid()
        leftPart = node["p"][:midIdx]
        rightPart = node["p"][midIdx:]
        rightChild = node["r"]
        node["p"] = leftPart
        node["r"] = int(newNid)
        self.put_node(nid, node)
        newNode = {"is_leaf": True, "m": 0, "p": rightPart, "r": rightChild}
        self.put_node(newNid, newNode)
        parentKey = rightPart[0]["key"]
        return parentKey, newNid
    
    def parent_insert(self, key, nidList, nid, newNid):
        if nidList == []:
            newRootid = self.get_nid()
            newRoot = {
                "is_leaf": False,
                "m": 0,
                "p": [{"key": key, "left_child_node": int(nid)}],
                "r": int(newNid)
            }
            self.put_node(newRootid, newRoot)
            self.set_rootid(newRootid)
            return
        parentid = nidList[-1]
        parentNode = self.get_node(parentid)
        idx = 0
        while idx < parentNode["m"] and parentNode["p"][idx]["key"] < key:
            idx += 1
        if idx == parentNode["m"]:
            parentNode["r"] = int(newNid)
        else:
            parentNode["p"][idx]["left_child_node"] = int(newNid)
        parentNode["p"].insert(idx, {"key": key, "left_child_node": int(nid)})
        self.put_node(parentid, parentNode)
        if parentNode["m"] >= self.n:
            self.split_internal(parentid, nidList[:-1])

    def split_internal(self, nid, nidList):
        node = self.get_node(nid)
        midIdx = math.floor(node["m"] / 2)
        newNid = self.get_nid()
        leftPart = node["p"][:midIdx]
        rightPart = node["p"][midIdx + 1:]
        midKey = node["p"][midIdx]["key"]
        leftRightChild = node["p"][midIdx]["left_child_node"]
        rightRightChild = node["r"]
        node["p"] = leftPart
        node["r"] = leftRightChild
        self.put_node(nid, node)
        newNode = {"is_leaf": False, "m": 0, "p": rightPart, "r": rightRightChild}
        self.put_node(newNid, newNode)
        self.parent_insert(midKey, nidList, nid, newNid)

    def delete(self, key):
        nid, nidList = self.find_leaf_node(key)
        node = self.get_node(nid)
        idx = 0
        while idx < node["m"] and key != node["p"][idx]["key"]:
            idx += 1
        if idx >= node["m"]:
            return
        rightNode = self.get_node(node["r"])
        rightKey = rightNode["p"][0]["key"]
        if idx < node["m"] - 1:
            rightKey = node["p"][idx + 1]["key"]
        del node["p"][idx]
        self.check_same(nidList, key, rightKey)
        self.put_node(nid, node)
        self.op_after_del(nid, nidList)
    
    def node_to_list(self, node):
        key = [pair["key"] for pair in node["p"]]
        child = [pair["left_child_node"] for pair in node["p"]] + [node["r"]]
        return key, child
    
    def list_to_node(self, key, child):
        pair = [{"key": key[i], "left_child_node": child[i]} for i in range(0, len(key))]
        node = {"is_leaf": False, "m": len(key), "p": pair, "r": child[-1]}
        return node
    
    def min_keys(self):
        if self.get_rootid() == "0":
            if self.get_node("0")["is_leaf"] == True:
                return 0
        return math.ceil(self.n / 2) - 1

    def op_after_del(self, nid, nidList):
        if nidList == []:
            rootNode = self.get_node(nid)
            if rootNode["is_leaf"] == False:
                key, child = self.node_to_list(rootNode)
                if len(child) == 1:
                    self.set_rootid(child[0])
                    del self.index["nodes"][nid]
            return
        node = self.get_node(nid)
        if node["is_leaf"] == True:
            if node["m"] >= self.min_keys():
                return
        else:
            if node["m"] >= math.ceil(self.n / 2) - 1:
                return
        pid = nidList[-1]
        parent = self.get_node(pid)
        parentKey, parentChild = self.node_to_list(parent)
        idx = parentChild.index(int(nid))
        if idx > 0:
            left_node = self.get_node(parentChild[idx - 1])
        else:
            left_node = None
        if idx < parent["m"]:
            right_node = self.get_node(parentChild[idx + 1])
        else:
            right_node = None
        if left_node != None:
            if left_node["m"] > self.min_keys():
                self.take_from_left(nid, parentChild[idx - 1], pid, idx)
            else:
                self.merge_with_left(nid, parentChild[idx - 1], pid, idx, nidList[:-1])
        else:
            if right_node["m"] > self.min_keys():
                self.take_from_right(nid, parentChild[idx + 1], pid, idx)
            else:
                self.merge_with_right(nid, parentChild[idx + 1], pid, idx, nidList[:-1])

    def check_same(self, nidList, key, rightKey):
        for nid in nidList:
            node = self.get_node(nid)
            nodeKey, nodeChild = self.node_to_list(node)
            for i, k in enumerate(nodeKey):
                if k == key:
                    node["p"][i]["key"] = rightKey
                    return

    def take_from_left(self, nid, leftNid, pid, idx):
        node = self.get_node(nid)
        leftNode = self.get_node(leftNid)
        parent = self.get_node(pid)
        if node["is_leaf"] == True:
            pair = leftNode["p"][-1]
            del leftNode["p"][-1]
            node["p"].insert(0, pair)
            parent["p"][idx - 1]["key"] = pair["key"]
            self.put_node(nid, node)
            self.put_node(leftNid, leftNode)
            self.put_node(pid, parent)
        else:
            newKey = parent["p"][idx - 1]["key"]
            parent["p"][idx - 1]["key"] = leftNode["p"][-1]["key"]
            newChild = leftNode["r"]
            leftNode["r"] = leftNode["p"][-1]["left_child_node"]
            del leftNode["p"][-1]
            node["p"].insert(0, {"key": newKey, "left_child_node": newChild})
            self.put_node(nid, node)
            self.put_node(leftNid, leftNode)
            self.put_node(pid, parent)

    def take_from_right(self, nid, rightNid, pid, idx):
        node = self.get_node(nid)
        rightNode = self.get_node(rightNid)
        parent = self.get_node(pid)
        if node["is_leaf"] == True:
            pair = rightNode["p"][0]
            del rightNode["p"][0]
            node["p"].append(pair)
            parent["p"][idx]["key"] = rightNode["p"][0]["key"]
            self.put_node(nid, node)
            self.put_node(rightNid, rightNode)
            self.put_node(pid, parent)
        else:
            newKey = parent["p"][idx]["key"]
            parent["p"][idx]["key"] = rightNode["p"][0]["key"]
            newChild = node["r"]
            node["r"] = rightNode["p"][0]["left_child_node"]
            del rightNode["p"][0]
            node["p"].append({"key": newKey, "left_child_node": newChild})
            self.put_node(nid, node)
            self.put_node(rightNid, rightNode)
            self.put_node(pid, parent)
        
    def merge_with_left(self, nid, leftNid, pid, idx, nidList):
        node = self.get_node(nid)
        leftNode = self.get_node(leftNid)
        parent = self.get_node(pid)
        parentKey, parentChild = self.node_to_list(parent)
        if node["is_leaf"] == True:
            leftNode["p"].extend(node["p"])
            leftNode["r"] = node["r"]
            del parentKey[idx - 1]
            del parentChild[idx]
            del self.index["nodes"][str(nid)]
            self.put_node(leftNid, leftNode)
            self.put_node(pid, self.list_to_node(parentKey, parentChild))
        else:
            leftKey, leftChild = self.node_to_list(leftNode)
            nodeKey, nodeChild = self.node_to_list(node)
            leftKey.append(parentKey[idx - 1])
            leftKey.extend(nodeKey)
            leftChild.extend(nodeChild)
            del parentKey[idx - 1]
            del parentChild[idx]
            del self.index["nodes"][str(nid)]
            self.put_node(leftNid, self.list_to_node(leftKey, leftChild))
            self.put_node(pid, self.list_to_node(parentKey, parentChild))
        self.op_after_del(pid, nidList)

    def merge_with_right(self, nid, rightNid, pid, idx, nidList):
        node = self.get_node(nid)
        rightNode = self.get_node(rightNid)
        parent = self.get_node(pid)
        parentKey, parentChild = self.node_to_list(parent)
        if node["is_leaf"] == True:
            node["p"].extend(rightNode["p"])
            node["r"] = rightNode["r"]
            del parentKey[idx]
            del parentChild[idx + 1]
            del self.index["nodes"][str(rightNid)]
            self.put_node(nid, node)
            self.put_node(pid, self.list_to_node(parentKey, parentChild))
        else:
            rightKey, rightChild = self.node_to_list(rightNode)
            nodeKey, nodeChild = self.node_to_list(node)
            nodeKey.append(parentKey[idx])
            nodeKey.extend(rightKey)
            nodeChild.extend(rightChild)
            del parentKey[idx]
            del parentChild[idx + 1]
            del self.index["nodes"][str(rightNid)]
            self.put_node(nid, self.list_to_node(nodeKey, nodeChild))
            self.put_node(pid, self.list_to_node(parentKey, parentChild))
        self.op_after_del(pid, nidList)

    def single_key_search(self, key):
        leafNid, nidList = self.find_leaf_node(key)
        for nid in nidList:
            node = self.get_node(nid)
            for pair in node["p"]:
                if pair == node["p"][-1]:
                    print(pair["key"])
                else:
                    print(pair["key"], ",", end = " ")
        leafNode = self.get_node(leafNid)
        for pair in leafNode["p"]:
            if pair["key"] == key:
                print(pair["value"])
                return
        print("NOT FOUND")

    def range_search(self, skey, ekey):
        leafNid, nidList = self.find_leaf_node(skey)
        leafNode = self.get_node(leafNid)
        idx = 0
        while idx < leafNode["m"] and leafNode["p"][idx]["key"] < skey:
            idx += 1
        while True:
            while idx < leafNode["m"] and leafNode["p"][idx]["key"] <= ekey:
                print(leafNode["p"][idx]["key"], ",", leafNode["p"][idx]["value"])
                idx += 1
            if leafNode["r"] == None:
                break
            if idx >= leafNode["m"]:
                idx = 0
                leafNode = self.get_node(str(leafNode["r"]))
                continue
            if leafNode["p"][idx]["key"] > ekey:
                break
    
def create_data_file(n: int):
    return {
        "n": int(n),
        "root": 0,
        "next_nid": 1,
        "nodes": {
            "0": {
                "is_leaf": True,
                "m": 0,
                "p": [],
                "r": None
            }
        }
    }

def create_data(index_file, b):
    data.save(index_file, create_data_file(b))

def insert_data(index_file, data_file):
    index = data.load(index_file)
    tree = Bptree(index)
    with open(data_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for line in reader:
            if line == []:
                continue
            else:
                tree.insert(int(line[0].strip()), int(line[1].strip()))
    data.save(index_file, tree.index)

def delete_data(index_file, data_file):
    index = data.load(index_file)
    tree = Bptree(index)
    with open(data_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for line in reader:
            if line == []:
                continue
            else:
                tree.delete(int(line[0].strip()))
    data.save(index_file, tree.index)

def single_key_search_data(index_file, key):
    index = data.load(index_file)
    tree = Bptree(index)
    tree.single_key_search(key)

def range_search_data(index_file, skey, ekey):
    index = data.load(index_file)
    tree = Bptree(index)
    tree.range_search(skey, ekey)

def parse_args(argv):
    parser = argparse.ArgumentParser(prog = "bptree")
    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument("-c", nargs=2, metavar=("index_file", "b"))
    group.add_argument("-i", nargs=2, metavar=("index_file", "data_file"))
    group.add_argument("-d", nargs=2, metavar=("index_file", "data_file"))
    group.add_argument("-s", nargs=2, metavar=("index_file", "key"))
    group.add_argument("-r", nargs=3, metavar=("index_file", "start_key", "end_key"))
    return parser.parse_args(argv)

def main(argv = None):
    if argv is None:
        argv = sys.argv[1:]
    parsed_args = parse_args(argv)
    if parsed_args.c:
        create_data(parsed_args.c[0], int(parsed_args.c[1]))
    elif parsed_args.i:
        insert_data(parsed_args.i[0], parsed_args.i[1])
    elif parsed_args.d:
        delete_data(parsed_args.d[0], parsed_args.d[1])
    elif parsed_args.s:
        single_key_search_data(parsed_args.s[0], int(parsed_args.s[1]))
    elif parsed_args.r:
        range_search_data(parsed_args.r[0], int(parsed_args.r[1]), int(parsed_args.r[2]))

if __name__ == "__main__":
    main()
