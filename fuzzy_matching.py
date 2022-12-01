""" Fuzzy Matching
Easy and fast fuzzy/approximate matching of single strings against large collections of strings.

Create and manage libraries with the Stringlib class and add collections of strings to them. Some common pre-processing
options can be applied per collection. Run queries against combinations of collections and get returned the
top n matches with their respective: collection-name, pre- and post-processing string, related value (if provided)
and ratio of the match.

Requires the RapidFuzz package.

Basic usage with default settings:
    import fuzzy_matching as fm

    lib1 = fm.StringLib()
    lib1.add_col(['Netherlands', 'Germany', 'France', 'Spain'], 'world countries')
    ukdict = {'London': 'london.uk/page.html', 'Edinburgh': 'pop 500.000', 'Manchester': 'plays football', 'Birmingham': '', 'Glasgow': 'D:\Glasgow\'}
    lib1.add_col(ukdict, 'uk cities with meta')

    results_dict = lib1.get_top('testme')


For reference on a 2020 laptop (Python v3.11):
Compares a 28 character string to 1.000.000+ strings in about 340ms.
Compares a 10 character string to ~200.000 strings in about 45ms.
Compares a 6 character string to 60.000+ strings in about 15ms.
"""


from unicodedata import normalize
from time import perf_counter_ns
from rapidfuzz import fuzz, process


class StringLib:
    """ String Library
    Manage collections of strings and run fuzzy/approximate queries against them.
    """
    __slots__ = '__strlib'

    def __init__(self):
        self.__strlib = {'collections': [], 'total_strings': 0}

    def __str__(self):
        total_refs = 0
        for collection in self.collections():
            total_refs += self.__strlib[collection]['num_ref']
        return f"String Library holding {total_refs} references in {len(self.collections())} collections"

    def add_col(self, collection: list[str] | dict, label: str,
                ignore_case: bool = True,
                to_ascii: bool = True,
                no_strip: bool = False):
        """ Add a collection to this library

        Argumenting a list as collection will make matches return an empty string as relation. Argumenting a dict as
        collection will run matches against the keys and also return the associated values.

        :param collection: A list or dictionary of strings to run matches against. Using a dict here will expect the key
               to be the reference string. The value can be of any type and will be returned along with the reference
               in case of a match.
        :param label: The name of this collection.
        :param ignore_case: Specify whether to ignore character cases when querying this collection. (default=True)
        :param to_ascii: Specify whether to try and convert any non-ASCII character to ASCII first before querying
                         (ie: ë to e, etc.). (default=True)
        :param no_strip: Specify whether to strip strings from preceeding and trailing whitespace characters when
                         querying this collection. (default=False)
        """
        # LBYL checks
        if type(label) is not str:
            raise TypeError(f"'label' argument is not a string: {label}")
        if type(ignore_case) is not bool:
            raise TypeError(f"'ignore_case' argument is not a boolean: {ignore_case}")
        if type(to_ascii) is not bool:
            raise TypeError(f"'to_ascii' argument is not a boolean: {to_ascii}")
        if type(no_strip) is not bool:
            raise TypeError(f"'no_strip' argument is not a boolean: {no_strip}")
        if type(collection) is not list and type(collection) is not dict:
            raise TypeError(f"'collection' argument is not a list or dictionary")
        islist = False
        if len(collection) > 1:
            if type(collection) is list:
                islist = True
                for item in collection:
                    if not isinstance(item, str):
                        raise TypeError(f"'collection' list contains a non-string item: {item}")
        else:
            raise Exception(f"'collection' list or dictionary contains less than 2 items.")

        self.__strlib['collections'].append(label)
        self.__strlib[label] = {}
        self.__strlib[label]['ignore_case'] = ignore_case
        self.__strlib[label]['to_ascii'] = to_ascii
        self.__strlib[label]['no_strip'] = no_strip

        # Create and store base collection and values
        if islist:
            pre_col = collection.copy()
        else:
            pre_col = list(collection.keys())
        self.__strlib[label]['collection'] = pre_col

        len_col = len(pre_col)
        self.__strlib[label]['num_ref'] = len_col

        if islist:
            values = [''] * len_col
        else:
            values = list(collection.values())
        self.__strlib[label]['values'] = values

        # creates potential misalignments
        # while "" in pre_col:
        #     pre_col.remove("")
        # while "\n" in pre_col:
        #     pre_col.remove("\n")

        # Pre-processing
        if not no_strip:
            pre_col = [item.strip() for item in pre_col]

        if to_ascii:
            if ignore_case:
                references = [normalize("NFKD", item).encode("ascii", "ignore").decode().lower() for item in pre_col]
            else:
                references = [normalize("NFKD", item).encode("ascii", "ignore").decode() for item in pre_col]
        else:
            if ignore_case:
                references = [item.lower() for item in pre_col]
            else:
                references = pre_col.copy()

        # Create dicts with everything grouped by length
        self.__strlib[label]['col_by_len'] = {}
        self.__strlib[label]['ref_by_len'] = {}
        self.__strlib[label]['val_by_len'] = {}
        for i, ref in enumerate(references):
            length = len(ref)
            self.__strlib[label]['col_by_len'].setdefault(length, []).append(pre_col[i])
            self.__strlib[label]['ref_by_len'].setdefault(length, []).append(ref)
            self.__strlib[label]['val_by_len'].setdefault(length, []).append(values[i])

    def del_col(self, label: str):
        """ Delete a collection from this library
        :param label: Name of the collection to delete.
        """
        if type(label) is not str:
            raise TypeError(f"'label' argument is not a string: {label}")
        self.__strlib.pop(label, None)
        self.__strlib['collections'].remove(label)

    def ren_col(self, old_label: str, new_label: str):
        """ Rename a collection
        :param old_label: Current name of the collection.
        :param new_label: New name of the collection.
        """
        if type(old_label) is not str:
            raise TypeError(f"'old_label' argument is not a string: {old_label}")
        if type(new_label) is not str:
            raise TypeError(f"'new_label' argument is not a string: {new_label}")
        try:
            self.__strlib[new_label] = self.__strlib.pop(old_label)
            self.__strlib['collections'].remove(old_label)
            self.__strlib['collections'].append(new_label)
        except KeyError:
            print(f"\nError: Collection not found: {old_label}")

    def set_pre_opt(self, label: str, ignore_case: bool = None, to_ascii: bool = None, no_strip: bool = None):
        """ Change the pre-processing settings for an existing collection
        :param label: Name of the collection to be changed.
        :param ignore_case: New setting for ignoring character cases.
        :param to_ascii: New setting for changing characters to an ascii equivalent.
        :param no_strip: New setting for stripping preceeding and trailing whitespace
        """
        if ignore_case is None and to_ascii is None and no_strip is None:
            return

        if type(label) is not str:
            raise TypeError(f"'label' argument is not a string: {label}")
        cols = self.collections()
        if len(cols) == 0:
            raise KeyError(f"Library is empty")
        if label not in self.__strlib:
            raise KeyError(f"Collection not found: {label}")
        if ignore_case is None:
            ignore_case = self.__strlib[label]['ignore_case']
        else:
            if type(ignore_case) is not bool:
                raise TypeError(f"'ignore_case' argument is not a boolean: {ignore_case}")
        if to_ascii is None:
            to_ascii = self.__strlib[label]['to_ascii']
        else:
            if type(to_ascii) is not bool:
                raise TypeError(f"'to_ascii' argument is not a boolean: {to_ascii}")
        if no_strip is None:
            no_strip = self.__strlib[label]['no_strip']
        else:
            if type(no_strip) is not bool:
                raise TypeError(f"'no_strip' argument is not a boolean: {no_strip}")

        if self.__strlib[label]['ignore_case'] == ignore_case and self.__strlib[label]['to_ascii'] == to_ascii \
                and self.__strlib[label]['no_strip'] == no_strip:
            return

        temp_col = dict(zip(self.__strlib[label]['collection'], self.__strlib[label]['values']))

        self.del_col(label)
        self.add_col(temp_col, label, ignore_case=ignore_case, to_ascii=to_ascii, no_strip=no_strip)

    def col_info(self, label: str, full: bool = False) -> dict:
        """ Get information about a collection
        :param label: Name of the collection.
        :param full: When True return includes the string list. (default=False)
        :return: A dict containing information about the collection.
        """
        if type(label) is not str:
            raise TypeError(f"'label' argument is not a string: {label}")
        cols = self.collections()
        if len(cols) == 0:
            raise KeyError(f"Library is empty")
        if label not in self.__strlib:
            raise KeyError(f"Collection not found: {label}")

        info = {'label': label,
                'ignore_case': self.__strlib[label]['ignore_case'],
                'to_ascii': self.__strlib[label]['to_ascii'],
                'no_strip': self.__strlib[label]['no_strip'],
                'num_strings': self.__strlib[label]['num_ref']}
        if full:
            collection = []
            for length, value in self.__strlib[label]['col_by_len'].items():
                for i, pre_col in enumerate(value):
                    collection.append((pre_col, self.__strlib[label]['ref_by_len'][length][i], self.__strlib[label]['val_by_len'][length][i]),)
            info['collection'] = collection
        return info

    def collections(self) -> list[str]:
        """ Get a list of collection names in this library
        :return: A list of collection names in this library.
        """
        return self.__strlib['collections']

    def clr_lib(self):
        """ Clear this library
        """
        self.__strlib = {'collections': [], 'total_strings': 0}

    def lib_info(self) -> dict:
        """ Get information about this library
        :return: A dict with information about this library.
        """
        collections = self.collections()
        info = {'collections': collections}
        tot_refs = 0
        for collection in collections:
            tot_refs += self.__strlib[collection]['num_ref']
            info[collection] = {}
            info[collection]['num_strings'] = self.__strlib[collection]['num_ref']
            info[collection]['ignore_case'] = self.__strlib[collection]['ignore_case']
            info[collection]['to_ascii'] = self.__strlib[collection]['to_ascii']
            info[collection]['no_strip'] = self.__strlib[collection]['no_strip']
        info['total_strings'] = tot_refs
        return info

    def get_top(self, query: str,
                collections: list[str] = None,
                top: int = 1,
                look_around: int = -1,
                lmin: int = 1,
                lmax: int = 0
                ) -> dict | None:
        """ Get the top x best matches
        :param query: A string to match against one or more collections from this library.
        :param collections: A list of collection names to match against. If None uses all collections. (default=None)
        :param top: The amount of best matches to return. Set to 0 for all(!) results. (default=1)
        :param look_around: Set a limit to how many characters longer or shorter a (collection-) string may be before
               skipping it. Set to -1 for no limit. (default=-1)
        :param lmin: Set a minimum character length for strings to compare your query to. (default=1)
        :param lmax: Set a maximum character length for strings to compare your query to. Set to 0 for no maximum. (default=0)
        :return: A dictionary with results and some stats about the search.
        """
        # LBYL checks
        if query.strip() == "" or query is None:
            return None
        if type(query) is not str:
            raise TypeError(f"'query' argument is not a string: {query}")
        if collections:
            if type(collections) is not list:
                raise TypeError(f"'collections' argument is not a list: {collections}")
            for collection in collections:
                if type(collection) is not str:
                    raise TypeError(f"'collections' argument list contains a non-string object: {collection}")
                if collection not in self.__strlib:
                    raise KeyError(f"Collection not found: {collection}")
        else:
            collections = self.collections()
        if type(top) is not int:
            raise TypeError(f"'top' argument is not an integer: {top}")
        if top < 0:
            raise ValueError(f"'top' argument must be 0 or greater: ({top} < 0)")
        if type(look_around) is not int:
            raise TypeError(f"'look_around' argument is not an integer: {look_around}")
        if look_around < -1:
            raise ValueError(f"'look_around' argument may not be smaller than -1: ({look_around} < -1)")
        if type(lmin) is not int:
            raise TypeError(f"'lmin' argument is not an integer: {lmin}")
        if lmin < 1:
            raise ValueError(f"'lmin' argument may not be smaller than 1: ({lmin} < 1)")
        if type(lmax) is not int:
            raise TypeError(f"'lmax' argument is not an integer: {lmax}")
        if lmax < 0:
            raise ValueError(f"'lmax' argument may not be smaller than 0: ({lmax} < 0)")

        if top == 0:
            top = None
        results = {'query': query, 'skipped': 0, 'total': 0}
        st_t0 = perf_counter_ns()

        # do matching for each argumented collection
        temp_results = []
        for collection in collections:
            # apply collection pre-processing settings to query
            if self.__strlib[collection]['ignore_case']:
                query = query.lower()
            if self.__strlib[collection]['to_ascii']:
                query = normalize("NFKD", query).encode("ascii", "ignore").decode()
            if not self.__strlib[collection]['no_strip']:
                query = query.strip()

            results['total'] += self.__strlib[collection]['num_ref']

            # do matching per word length
            len_query = len(query)
            for length, ref_list in self.__strlib[collection]['ref_by_len'].items():
                # skip string set if its character length is smaller than lmin
                if length < lmin:
                    results['skipped'] += len(self.__strlib[collection]['ref_by_len'][length])
                    continue

                # skip string set if its character length is bigger than lmax
                if lmax != 0:
                    if length > lmax:
                        results['skipped'] += len(self.__strlib[collection]['ref_by_len'][length])
                        continue

                # skip string set if its character length is out of look_around range
                if look_around > -1:
                    if abs(length - len_query) > look_around:
                        results['skipped'] += len(self.__strlib[collection]['ref_by_len'][length])
                        continue

                # get a list of ratios for this string set
                ratios = process.extract(query, ref_list, scorer=fuzz.ratio, limit=top)

                for ratio in ratios:
                    result = (self.__strlib[collection]['col_by_len'][length][ratio[2]], collection, ratio[0],
                              self.__strlib[collection]['val_by_len'][length][ratio[2]], ratio[1]),
                    temp_results.extend(result)

        # finalize results and stats
        temp_results.sort(key=lambda x: x[4], reverse=True)
        if top != 0:
            results['results'] = temp_results[:top]
        else:
            results['results'] = temp_results
        results['collections'] = collections
        results['tested'] = results['total'] - results['skipped']
        results['time'] = round((perf_counter_ns() - st_t0) / 1e6)
        return results


