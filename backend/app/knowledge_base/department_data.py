"""Recipient knowledge base used to resolve noisy printed and handwritten OCR."""

DEPARTMENT_DATA = [
    {"faculty_id": "vv", "faculty_name": "Venkatachala V", "aliases": ["VV", "Venky", "Venkatachala"]},
    {"faculty_id": "vp", "faculty_name": "Vijay Patil", "aliases": ["VP", "Vijay P"]},
    {"faculty_id": "vvp", "faculty_name": "Vijay Veerabhadra Patil", "aliases": ["VVP", "Vijay V Patil"]},
    {"faculty_id": "vlk", "faculty_name": "Vijay Kumar L K", "aliases": ["VLK", "Vijay Kumar", "Vijay L K"]},
    {"faculty_id": "abc", "faculty_name": "Ananya Bhat", "aliases": ["AB", "Ananya"]},
    {"faculty_id": "rsk", "faculty_name": "Ravi Shankar K", "aliases": ["RSK", "Ravi Shankar"]},
    {"faculty_id": "mkr", "faculty_name": "Meghana Rao", "aliases": ["MR", "Meghana"]},
    {"faculty_id": "skp", "faculty_name": "Suresh Kumar P", "aliases": ["SKP", "Suresh"]},
    {"faculty_id": "nrs", "faculty_name": "Nandini R S", "aliases": ["NRS", "Nandini"]},
    {"faculty_id": "dpm", "faculty_name": "Deepak M", "aliases": ["DPM", "Deepak"]},
    {"faculty_id": "krs", "faculty_name": "Kiran S", "aliases": ["KS", "Kiran"]},
    {"faculty_id": "pvn", "faculty_name": "Priya V N", "aliases": ["PVN", "Priya"]},
    {"faculty_id": "gms", "faculty_name": "Ganesh M S", "aliases": ["GMS", "Ganesh"]},
    {"faculty_id": "tpk", "faculty_name": "Tejaswini P K", "aliases": ["TPK", "Tejaswini"]},
    {"faculty_id": "srd", "faculty_name": "Shivraj R D", "aliases": ["SRD", "Shivraj"]},
    {
        "faculty_id": "students",
        "faculty_name": "Students",
        "aliases": ["Student", "All students", "Student group", "Students group"],
        "kind": "group",
        "description": "All students; route to the configured student email group.",
    },
    {
        "faculty_id": "file",
        "faculty_name": "File",
        "aliases": ["File copy", "For file", "File record"],
        "kind": "non_recipient",
        "description": "A filing instruction; add the circular to the file and do not email it as a recipient.",
    },
]

