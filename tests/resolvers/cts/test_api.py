from MyCapytain.resolvers.cts.api import HttpCTSResolver
from MyCapytain.retrievers.cts5 import CTS
from MyCapytain.common.utils import xmlparser
from MyCapytain.common.constants import NS, Mimetypes
from MyCapytain.common.metadata import Metadatum
from MyCapytain.resources.prototypes.text import Passage
from MyCapytain.resources.collections.cts import TextInventory, TextGroup, Work, Text
from MyCapytain.resources.prototypes.metadata import Collection

from unittest import TestCase
from mock import MagicMock


with open("tests/testing_data/cts/getpassage.xml") as f:
    GET_PASSAGE = xmlparser(f)
with open("tests/testing_data/cts/getpassageplus.xml") as f:
    GET_PASSAGE_PLUS = xmlparser(f)
with open("tests/testing_data/cts/getprevnexturn.xml") as f:
    NEXT_PREV = xmlparser(f)
with open("tests/testing_data/cts/getprevnexturn.nextonly.xml") as f:
    NEXT = xmlparser(f)
with open("tests/testing_data/cts/getprevnexturn.prevonly.xml") as f:
    PREV = xmlparser(f)
with open("tests/testing_data/cts/getValidReff.xml") as f:
    GET_VALID_REFF_FULL = xmlparser(f)
with open("tests/testing_data/cts/getValidReff.1.1.xml") as f:
    GET_VALID_REFF = xmlparser(f)
with open("tests/testing_data/cts/getCapabilities.xml") as f:
    GET_CAPABILITIES = xmlparser(f)
with open("tests/testing_data/cts/getCapabilities1294002.xml") as f:
    GET_CAPABILITIES_FILTERED = xmlparser(f)
with open("tests/testing_data/cts/getPassageOtherTest.xml") as f:
    GET_PASSAGE_CITATION_FAILURE = f.read()


class TestHttpCTSResolver(TestCase):
    def setUp(self):
        self.resolver = HttpCTSResolver(CTS("http://localhost"))
        self.resolver.endpoint.getPassagePlus = MagicMock(return_value=GET_PASSAGE_PLUS)
        self.resolver.endpoint.getPassage = MagicMock(return_value=GET_PASSAGE)
        self.resolver.endpoint.getPrevNextUrn = MagicMock(return_value=NEXT_PREV)
        self.resolver.endpoint.getValidReff = MagicMock(return_value=GET_VALID_REFF)
        self.resolver.endpoint.getCapabilities = MagicMock(return_value=GET_CAPABILITIES)

    def test_getPassage_full(self):
        """ Test that we can get a full text """
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2")

        # We check we made a reroute to GetPassage request
        self.resolver.endpoint.getPassage.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"
        )
        self.assertIsInstance(
            passage, Passage,
            "GetPassage should always return passages objects"
        )

        children = list(passage.getReffs())

        # We check the passage is able to perform further requests and is well instantiated
        self.resolver.endpoint.getValidReff.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2",
            level=1
        )
        self.assertEqual(
            children[0], '1.1.1',
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export Text should work correctly"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.PYTHON.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=NS, magic_string=False),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_subreference(self):
        """ Test that we can get a subreference text passage"""
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2", "1.1")

        # We check we made a reroute to GetPassage request
        self.resolver.endpoint.getPassage.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
        )
        self.assertIsInstance(
            passage, Passage,
            "GetPassage should always return passages objects"
        )

        children = list(passage.getReffs())

        # We check the passage is able to perform further requests and is well instantiated
        self.resolver.endpoint.getValidReff.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            level=3
        )
        self.assertEqual(
            children[0], '1.1.1',
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export Text should work correctly"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.PYTHON.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=NS, magic_string=False),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_full_metadata(self):
        """ Test that we can get a full text with its metadata"""
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2", metadata=True)

        # We check we made a reroute to GetPassage request
        self.resolver.endpoint.getPassagePlus.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"
        )
        self.assertIsInstance(
            passage, Passage,
            "GetPassage should always return passages objects"
        )
        self.assertIsInstance(
            passage.about.metadata["title"], Metadatum
        )
        self.assertEqual(
            passage.metadata["title"]["eng"], "Epigrammata",
            "CTS API Remote HTTP Response should be correctly parsed"
        )
        self.assertEqual(
            passage.metadata["groupname"]["eng"], "Martial",
            "CTS API Remote HTTP Response should be correctly parsed"
        )
        self.assertEqual(
            passage.metadata["label"]["eng"], "M. Valerii Martialis Epigrammaton libri / recognovit W. Heraeus",
            "CTS API Remote HTTP Response should be correctly parsed"
        )
        self.assertEqual(
            passage.citation.name, "book",
            "CTS API Remote HTTP Response should be correctly parsed"
        )
        self.assertEqual(
            len(passage.citation), 3,
            "CTS API Remote HTTP Response should be correctly parsed"
        )

        children = list(passage.getReffs())

        # We check the passage is able to perform further requests and is well instantiated
        self.resolver.endpoint.getValidReff.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2",
            level=1
        )
        self.assertEqual(
            children[0], '1.1.1',
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export Text should work correctly"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.PYTHON.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=NS, magic_string=False),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_prevnext(self):
        """ Test that we can get a full text with its metadata"""
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.1", metadata=True)

        # We check we made a reroute to GetPassage request
        self.resolver.endpoint.getPassagePlus.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
        )
        self.assertIsInstance(
            passage, Passage,
            "GetPassage should always return passages objects"
        )
        self.assertEqual(
            passage.prevId, "1.pr",
            "Previous Passage ID should be parsed"
        )
        self.assertEqual(
            passage.nextId, "1.2",
            "Next Passage ID should be parsed"
        )
        children = list(passage.getReffs())

        _ = passage.next
        self.resolver.endpoint.getPassage.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.2"
        )
        _ = passage.prev
        self.resolver.endpoint.getPassage.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr"
        )

        # We check the passage is able to perform further requests and is well instantiated
        self.resolver.endpoint.getValidReff.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            level=3
        )
        self.assertEqual(
            children[0], '1.1.1',
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export Text should work correctly"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.PYTHON.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=NS, magic_string=False),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_metadata_prevnext(self):
        """ Test that we can get a full text with its metadata"""
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.1", metadata=True, prevnext=True)

        # We check we made a reroute to GetPassage request
        self.resolver.endpoint.getPassagePlus.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
        )
        self.assertIsInstance(
            passage, Passage,
            "GetPassage should always return passages objects"
        )
        self.assertIsInstance(
            passage.about.metadata["title"], Metadatum
        )
        self.assertEqual(
            passage.metadata["title"]["eng"], "Epigrammata",
            "CTS API Remote HTTP Response should be correctly parsed"
        )
        self.assertEqual(
            passage.metadata["groupname"]["eng"], "Martial",
            "CTS API Remote HTTP Response should be correctly parsed"
        )
        self.assertEqual(
            passage.metadata["label"]["eng"], "M. Valerii Martialis Epigrammaton libri / recognovit W. Heraeus",
            "CTS API Remote HTTP Response should be correctly parsed"
        )
        self.assertEqual(
            passage.citation.name, "book",
            "CTS API Remote HTTP Response should be correctly parsed"
        )
        self.assertEqual(
            len(passage.citation), 3,
            "CTS API Remote HTTP Response should be correctly parsed"
        )
        self.assertEqual(
            passage.prevId, "1.pr",
            "Previous Passage ID should be parsed"
        )
        self.assertEqual(
            passage.nextId, "1.2",
            "Next Passage ID should be parsed"
        )
        children = list(passage.getReffs())

        _ = passage.next
        self.resolver.endpoint.getPassage.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.2"
        )
        _ = passage.prev
        self.resolver.endpoint.getPassage.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr"
        )

        # We check the passage is able to perform further requests and is well instantiated
        self.resolver.endpoint.getValidReff.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            level=3
        )
        self.assertEqual(
            children[0], '1.1.1',
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export Text should work correctly"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.PYTHON.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=NS, magic_string=False),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getMetadata_full(self):
        """ Checks retrieval of Metadata information """
        metadata = self.resolver.getMetadata()
        self.resolver.endpoint.getCapabilities.assert_called_with()
        self.assertIsInstance(
            metadata, Collection,
            "Resolver should return a collection object"
        )
        self.assertIsInstance(
            metadata.members[0], TextGroup,
            "Members of Inventory should be TextGroups"
        )
        self.assertEqual(
            len(metadata.descendants), 32,
            "There should be as many descendants as there is edition, translation, works and textgroup"
        )
        self.assertEqual(
            len(metadata.readableDescendants), 28,
            "There should be as many readable descendants as there is edition, translation, works"
        )
        self.assertEqual(
            len([x for x in metadata.readableDescendants if isinstance(x, Text)]), 15,
            "There should be 14 editions + 1 translations in readableDescendants"
        )
        self.assertEqual(
            len(metadata.export(output=Mimetypes.PYTHON.ETREE).xpath("//ti:edition[@urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2']", namespaces=NS)), 1,
            "There should be one node in exported format corresponding to lat2"
        )
        self.assertCountEqual(
            [x["@id"] for x in metadata.export(output=Mimetypes.JSON.DTS.Std)["http://w3id.org/dts-ontology/members"]],
            ["urn:cts:latinLit:phi1294", "urn:cts:latinLit:phi0959", "urn:cts:greekLit:tlg0003", "urn:cts:latinLit:phi1276"],
            "There should be 4 Members in DTS JSON"
        )

    def test_getMetadata_subset(self):
        """ Checks retrieval of Metadata information """
        self.resolver.endpoint.getCapabilities = MagicMock(return_value=GET_CAPABILITIES_FILTERED)
        metadata = self.resolver.getMetadata(objectId="urn:cts:latinLit:phi1294.phi002")
        self.resolver.endpoint.getCapabilities.assert_called_with(urn="urn:cts:latinLit:phi1294.phi002")
        self.assertIsInstance(
            metadata, Collection,
            "Resolver should return a collection object (specifically here a Work)"
        )
        self.assertIsInstance(
            metadata.members[0], Text,
            "Members of Work should be TextGroups"
        )
        self.assertEqual(
            len(metadata.descendants), 2,
            "There should be as many descendants as there is edition, translation"
        )
        self.assertEqual(
            len(metadata.readableDescendants), 2,
            "There should be 1 edition + 1 translation in readableDescendants"
        )
        self.assertEqual(
            len([x for x in metadata.readableDescendants if isinstance(x, Text)]), 2,
            "There should be 1 edition + 1 translation in readableDescendants"
        )
        self.assertEqual(
            len(metadata.export(output=Mimetypes.PYTHON.ETREE).xpath("//ti:edition[@urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2']", namespaces=NS)), 1,
            "There should be one node in exported format corresponding to lat2"
        )
        self.assertCountEqual(
            [x["@id"] for x in metadata.export(output=Mimetypes.JSON.DTS.Std)["http://w3id.org/dts-ontology/members"]],
            ["urn:cts:latinLit:phi1294.phi002.perseus-lat2", "urn:cts:latinLit:phi1294.phi002.perseus-eng2"],
            "There should be one member in DTS JSON"
        )
        self.assertCountEqual(
            [
                x["http://www.w3.org/1999/02/22-rdf-syntax-ns#type"]
                for x in metadata.export(output=Mimetypes.JSON.DTS.Std) \
                    ["http://w3id.org/dts-ontology/capabilities"]\
                    ["http://w3id.org/dts-ontology/navigation"]\
                    ["http://w3id.org/dts-ontology/parents"]
                ],
            ["http://chs.harvard.edu/xmlns/cts/TextGroup", "http://chs.harvard.edu/xmlns/cts/TextInventory"],
            "There should be one member in DTS JSON"
        )

    def test_getSiblings(self):
        """ Ensure getSiblings works well """
        previous, nextious = self.resolver.getSiblings(
            textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.1"
        )
        self.resolver.endpoint.getPrevNextUrn.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
        )
        self.assertEqual(
            previous, "1.pr",
            "Previous should be well computed"
        )
        self.assertEqual(
            nextious, "1.2",
            "Previous should be well computed"
        )

    def test_getSiblings_nextOnly(self):
        """ Ensure getSiblings works well when there is only the next passage"""
        self.resolver.endpoint.getPrevNextUrn = MagicMock(return_value=NEXT)
        previous, nextious = self.resolver.getSiblings(
            textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.pr"
        )
        self.resolver.endpoint.getPrevNextUrn.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr"
        )
        self.assertEqual(
            previous, None,
            "Previous Should not exist"
        )
        self.assertEqual(
            nextious, "1.1",
            "Next should be well computed"
        )

    def test_getSiblings_prevOnly(self):
        """ Ensure getSiblings works well when there is only the previous passage"""
        self.resolver.endpoint.getPrevNextUrn = MagicMock(return_value=PREV)
        previous, nextious = self.resolver.getSiblings(
            textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.1.6"
        )
        self.resolver.endpoint.getPrevNextUrn.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.6"
        )
        self.assertEqual(
            previous, "1.1.5",
            "Previous should be well computed"
        )
        self.assertEqual(
            nextious, None,
            "Next should not exist"
        )

    def test_getReffs_full(self):
        """ Ensure getReffs works well """
        self.resolver.endpoint.getValidReff = MagicMock(return_value=GET_VALID_REFF_FULL)
        reffs = self.resolver.getReffs(textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", level=1)
        self.resolver.endpoint.getValidReff.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2", level=1
        )
        self.assertEqual(
            len(reffs), 9462,
            "There should be 9462 references"
        )
        self.assertEqual(
            reffs[0], "1.pr.1"
        )
        self.resolver.endpoint.getValidReff = MagicMock(return_value=GET_VALID_REFF_FULL)
        self.resolver.getReffs(textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", level=2)
        self.resolver.endpoint.getValidReff.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2", level=2
        )

        self.resolver.endpoint.getValidReff = MagicMock(return_value=GET_VALID_REFF)
        reffs = self.resolver.getReffs(textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1", level=1)
        self.resolver.endpoint.getValidReff.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1", level=3
        )
        self.assertEqual(
            len(reffs), 6,
            "There should be 6 references"
        )
        self.assertEqual(
            reffs[0], "1.1.1"
        )

    def test_citation_failure(self):
        """ Example for Resolver failed : some response have an issue with not available Citations ?
        """
        retriever = CTS("http://cts.dh.uni-leipzig.de/api/cts/")
        retriever.getPassage = MagicMock(return_value=GET_PASSAGE_CITATION_FAILURE)
        resolver = HttpCTSResolver(retriever)
        # We require a passage : passage is now a Passage object
        passage = resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2", "1.1")
        # We need an export as plaintext
        self.assertEqual(
            passage.export(output=Mimetypes.PLAINTEXT),
            "I Hic est quem legis ille, quem requiris, Toto notus in orbe Martialis Argutis epigrammaton libellis: \n"\
                " Cui, lector studiose, quod dedisti Viventi decus atque sentienti, Rari post cineres habent poetae. ",
            "Parsing should be successful"
        )
