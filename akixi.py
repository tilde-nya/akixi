import requests

class Akixi():
    def __init__(self, host, username, password, locale="en_GB"):
        """Create a session and logs in to Akixi reporting

        Parameters
        ----------
        host : str
            Name of Akixi host (https://<host>/akixi.com/CCS/API/v1)
        username : str
            Login username
        password : str
            Login password
        locale : str, default="en_GB"
            Locale used for HTTP authentication ("en_GB" or "en_US")

        Raises
        ------
        Exception
            If login request fails (Contains status code, reason)
        """
        self.URL = "https://" + host + ".akixi.com/CCS/API/v1"
        self.session = requests.Session()
        self.session.post(self.URL + "/session")

        r = self.session.get(self.URL + "/login", params={"locale": locale}, auth=(username, password))
        if r.status_code == 200 or ((r.status_code == 400) and (r.json()["Message"].startswith("There were other browser sessions active for"))):
            print("success")
            self.reports = []
            reports = self.session.get(self.URL + "/report").json()
            for i in reports:
                self.reports.append(Report(
                    session=self.session,
                    url=self.URL,
                    id=i["ID"],
                    type=i["Type"],
                    description=i["Description"].replace(u"\xa0", " "),
                    is_licensed=i["IsLicensed"],
                    is_binned=i["IsBinned"]
                ))
        else:
            print("not 200")
            print(r)
            print(r.text)
            raise Exception(r.status_code, r.reason)


    def logout(self):
        """Log out of Akixi

        Returns
        -------
        bool
            True if logout was successful
        """
        r = self.session.get(self.URL + "/logout")
        if r.status_code == 200:
            return True

    def list_reports(self):
        return self.reports

    def get_report(self, id):
        """Returns 1 report by its ID

        Parameters
        ----------
        id : str
            Unique ID of the report

        Returns
        -------
        Report
            Report object of the report

        Raises
        ------
        Exception
            If no report with the specified ID was found
        """
        for i in self.reports:
            if i.id == id:
                return i
        raise Exception()

class Report():
    """Akixi report

    Attributes
    ----------
    id : str
        Unique ID of report
    typeid : int
        Type of report
    typename : str
        Human-friendly type of report
    description : str
        Name of report (Including folders)
    is_licensed : bool
        True if user is licensed for the report
    is_binned : bool
        True if report is in the recycle bin
    """
    def __init__(self, session, url, id, type, description, is_licensed, is_binned):
        self.session = session
        self.URL = url
        self.id = id
        self.typeid = type
        try:
            self.typename = {
                0: "Active Call List",
                1: "Historic Call List",
                5: "Unreturned Lost Calls",
                20: "Extension List",
                21: "ACD Agent List",
                22: "Hunt Group List",
                23: "Trunk Interface List",
                40: "Calls By Tel No",
                41: "Calls By DDI",
                50: "Calls By ½ Hour Interval",
                51: "Calls By ½ Hour & Day",
                52: "Calls By Day",
                53: "Calls By Week",
                54: "Calls By Month",
                60: "Calls By Account Code",
                70: "ACD Activity Log",
                80: "ACD Not-Available Code List",
                100: "Desktop Wallboard",
                101: "External Content"
            }[type]
        except KeyError:
            self.typename = "Unknown"
        self.description = description
        self.is_licensed = is_licensed
        self.is_binned = is_binned

    def run(self):
        r = self.session.get(self.URL + "/report/" + requests.utils.quote(self.id) + "/exec")
        if "Message" in r.json():
            raise Exception(r.json()["Message"])
        else:
            return r.json()