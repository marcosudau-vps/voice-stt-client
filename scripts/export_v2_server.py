"""Export exact pinned Git blobs, avoiding archive's Windows EOL attributes.

Destination must be new. No checkout/branch or repository state is changed.
Create/use the qualification venv separately; it is never part of the export.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

SHA='ada13b011e1d3829f78e7f389e3b927795a2b3be'


def export(repository, destination):
    destination.mkdir(parents=True,exist_ok=False)
    entries=subprocess.check_output(['git','-C',str(repository),'ls-tree','-rz',SHA]).split(b'\0')
    blobs=[]
    for entry in entries:
        if not entry: continue
        meta,name=entry.split(b'\t',1); mode,kind,oid=meta.split()
        if kind==b'blob': blobs.append((oid,name.decode('utf8')))
    raw=subprocess.run(['git','-C',str(repository),'cat-file','--batch'],
        input=b'\n'.join(oid for oid,name in blobs)+b'\n',stdout=subprocess.PIPE,check=True).stdout
    position=0; hashes={}
    for oid,name in blobs:
        end=raw.index(b'\n',position); size=int(raw[position:end].split()[2])
        content=raw[end+1:end+1+size]; position=end+size+2
        path=destination/name
        if not path.resolve().is_relative_to(destination.resolve()):
            raise ValueError('unsafe Git path')
        path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(content)
        hashes[name]=hashlib.sha256(content).hexdigest()
    return dict(serverCommit=SHA,sourceHashes=hashes)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository',type=Path,required=True)
    parser.add_argument('--destination',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(export(args.repository,args.destination),indent=2))
