import pytest

pytestmark = [
    pytest.mark.tier(1)
    ]

@pytest.mark.polarion('CMP-111')
def test_nothing1():
    """
    bla1
    """
    print "1"


@pytest.mark.parametrize(('bla'),[
    pytest.mark.polarion('CMP-001') and pytest.mark.skip('skipping...') (1),
    pytest.mark.polarion('CMP-002') (2),
    pytest.mark.polarion('CMP-003') (3),
    pytest.mark.polarion('CMP-004', 'CMP-005') (4),
])
def test_nothing2(bla):
    """
    bla2
    """
    print "2"
