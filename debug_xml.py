import subprocess
import xml.etree.ElementTree as ET

# Get a sample event
result = subprocess.run(['wevtutil', 'qe', 'Application', '/count:1', '/format:xml'], 
                       capture_output=True, text=True)

print("RAW XML OUTPUT:")
print(result.stdout)
print("\n" + "="*50 + "\n")

# Parse the first event
event_xml = result.stdout.split('</Event>')[0] + '</Event>'
print("FIRST EVENT XML:")
print(event_xml)
print("\n" + "="*50 + "\n")

# Parse and test namespace handling
try:
    elem = ET.fromstring(event_xml)
    print("XML PARSED SUCCESSFULLY")
    
    # Test namespace
    namespace = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}
    
    # Try to find System element
    sys_elem_ns = elem.find('./ns:System', namespace)
    sys_elem_no_ns = elem.find('./System')
    
    print(f"System element with namespace: {sys_elem_ns is not None}")
    print(f"System element without namespace: {sys_elem_no_ns is not None}")
    
    # Use whichever works
    sys_elem = sys_elem_ns or sys_elem_no_ns
    
    if sys_elem is not None:
        print("\nTesting field extraction:")
        
        # Test EventID
        event_id_ns = sys_elem.find('./ns:EventID', namespace)
        event_id_no_ns = sys_elem.find('./EventID')
        event_id = event_id_ns or event_id_no_ns
        print(f"EventID element: {event_id}")
        if event_id is not None:
            print(f"EventID text: {event_id.text}")
        
        # Test Provider
        provider_ns = sys_elem.find('./ns:Provider', namespace)
        provider_no_ns = sys_elem.find('./Provider')
        provider = provider_ns or provider_no_ns
        print(f"Provider element: {provider}")
        if provider is not None:
            print(f"Provider Name: {provider.get('Name', 'No Name attribute')}")
        
        # Test Computer
        computer_ns = sys_elem.find('./ns:Computer', namespace)
        computer_no_ns = sys_elem.find('./Computer')
        computer = computer_ns or computer_no_ns
        print(f"Computer element: {computer}")
        if computer is not None:
            print(f"Computer text: {computer.text}")
            
        # Test TimeCreated
        time_ns = sys_elem.find('./ns:TimeCreated', namespace)
        time_no_ns = sys_elem.find('./TimeCreated')
        time_elem = time_ns or time_no_ns
        print(f"TimeCreated element: {time_elem}")
        if time_elem is not None:
            print(f"SystemTime: {time_elem.get('SystemTime', 'No SystemTime attribute')}")
    
except Exception as e:
    print(f"ERROR: {e}")
