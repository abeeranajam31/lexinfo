"""
Checks the Urdu base type examples against the built LexInfo ontology.

    python src/build-ontology.py > /tmp/lexinfo.owl
    python examples/urdu/check.py /tmp/lexinfo.owl

Fails if the examples use a LexInfo term that the ontology does not define,
or a base type value that is not a lexinfo:BaseType. Prints how many base
type uses are covered by LexInfo and which ones needed a local value.
"""
from rdflib import Graph, Namespace, RDF
from collections import Counter
import os
import sys

lexinfo = Namespace("http://www.lexinfo.net/ontology/3.0/lexinfo#")
morph = Namespace("http://www.w3.org/ns/lemon/morph#")

onto = Graph()
onto.parse(sys.argv[1] if len(sys.argv) > 1 else "ontology/3.0/lexinfo.owl")
data = Graph()
data.parse(os.path.join(os.path.dirname(__file__), "base-types.ttl"), format="turtle")

defined = set(onto.subjects())
errors = []

for term in set(data.all_nodes()) | set(data.predicates()):
    if str(term).startswith(str(lexinfo)) and term not in defined:
        errors.append("Undefined LexInfo term: %s" % term)

covered = Counter()
local = Counter()
for s, value in data.subject_objects(morph.baseType):
    if (value, RDF.type, lexinfo.BaseType) in onto:
        covered[value.split("#")[1]] += 1
    elif (value, RDF.type, lexinfo.BaseType) in data:
        local[value.split("#")[1]] += 1
    else:
        errors.append("%s has base type %s, which is not a lexinfo:BaseType" % (s, value))

print("Base type uses covered by LexInfo: %d" % sum(covered.values()))
for k, v in sorted(covered.items()):
    print("  lexinfo:%s  %d" % (k, v))
print("Base type uses needing a local value: %d" % sum(local.values()))
for k, v in sorted(local.items()):
    print("  %s  %d" % (k, v))

for e in errors:
    print("ERROR: " + e)
sys.exit(1 if errors else 0)
