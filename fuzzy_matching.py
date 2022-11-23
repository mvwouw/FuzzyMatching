""" Fuzzy Matching
Easy and fast fuzzy (approximate) matching of single strings against large collections of strings.

Create libraries with the Stringlib class and add collections of strings to them. Some common pre-processing options
are available and are applied per collection. Also present are some basic library and collection management methods.

Basic usage with default settings:
    lib1 = StringLib()
    lib1.add_col(['Netherlands', 'Germany', 'France', 'Spain'], 'world countries')
    lib1.add_col(['London', 'Edinburgh', 'Manchester', 'Birmingham', 'Glasgow'], 'uk cities')

    results_dict = lib1.top_from_col('testme')


For reference on a 2020 laptop:
Compares a 28 character string to more than 1.000.000 strings in about 600ms.
Compares a 10 character string to about 200.000 strings in about 70ms.
Compares a 6 character string to more than 60.000 strings in about 12ms.
"""


from unicodedata import normalize
from Levenshtein import ratio
from time import perf_counter_ns


class StringLib:
    """ String Library
    Manage collections of strings and run matches against them.
    """
    def __init__(self):
        self.__strlib = {'collections': [], 'total_strings': 0}

    def __str__(self):
        total_refs = 0
        for collection in self.collections():
            total_refs += self.__strlib[collection]['num_ref']
        return f"String Library holding {total_refs} references in {len(self.collections())} collections"

    def add_col(self, collection: list[str], label: str,
                ignore_case: bool = True,
                to_ascii: bool = True,
                no_strip: bool = False):
        """ Add a collection to this library

        :param collection: A list of strings to run matches against.
        :param label: The name of this collection.
        :param ignore_case: Specify whether to ignore character cases when matching against this collection.
        :param to_ascii: Specify whether to try and convert any non-ASCII character to ASCII first before matching
                         (ie: ë to e, etc.).
        :param no_strip: Specify whether to strip strings from preceeding and trailing whitespace characters when
                         matching against this collection.
        """
        # LBYL checks
        if type(label) is not str:
            raise TypeError(f"'label' argument is not a string: {label}")
        if type(ignore_case) is not bool:
            raise TypeError(f"'ignore_case' argument is not a boolean: {ignore_case}")
        if type(to_ascii) is not bool:
            raise TypeError(f"'to_ascii' argument is not a boolean: {to_ascii}")
        if type(collection) is not list:
            raise TypeError(f"'collection' argument is not a list")
        if len(collection) > 1:
            for item in collection:
                if not isinstance(item, str):
                    raise TypeError(f"'collection' list contains a non-string item: {item}")
        else:
            raise Exception(f"'collection' list contains less than 2 strings.")

        self.__strlib['collections'].append(label)
        self.__strlib[label] = {}
        self.__strlib[label]['ignore_case'] = ignore_case
        self.__strlib[label]['to_ascii'] = to_ascii
        self.__strlib[label]['no_strip'] = no_strip

        # Pre-processing
        if not no_strip:
            collection = [item.strip() for item in collection]
        while "" in collection:
            collection.remove("")
        while "\n" in collection:
            collection.remove("\n")
        if to_ascii:
            if ignore_case:
                reference = [normalize("NFKD", item).encode("ascii", "ignore").decode().lower() for item in collection]
            else:
                reference = [normalize("NFKD", item).encode("ascii", "ignore").decode() for item in collection]
        else:
            if ignore_case:
                reference = [item.lower() for item in collection]
            else:
                reference = collection.copy()
        len_col = len(reference)
        self.__strlib[label]['num_ref'] = len_col

        # Create dict with strings grouped by length
        label_list = [label] * len_col
        col_ref = zip(collection, label_list, reference)
        self.__strlib[label]['col_by_len'] = {}
        for tup in col_ref:
            self.__strlib[label]['col_by_len'].setdefault(len(tup[2]), []).append(tup)

    def del_col(self, label: str):
        """ Delete a collection from this library
        :param label: Name of the collection to be deleted.
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

    def col_info(self, label: str, full: bool = False) -> dict | None:
        """ Get information about a collection
        :param label: Name of the collection.
        :param full: When True returns the string list aswell.
        :return: A dict containing information about the collection. Returns None if the library is empty.
        """
        if type(label) is not str:
            raise TypeError(f"'label' argument is not a string: {label}")
        cols = self.collections()
        if len(cols) == 0:
            return None

        info = {'label': label}
        try:
            info['ignore_case'] = self.__strlib[label]['ignore_case']
            info['to_ascii'] = self.__strlib[label]['to_ascii']
            info['no_strip'] = self.__strlib[label]['no_strip']
            info['num_strings'] = self.__strlib[label]['num_ref']
            if full:
                collection = []
                for _, value in self.__strlib[label]['col_by_len'].items():
                    for ref in value:
                        collection.append(ref)
                info['collection'] = collection
            return info
        except KeyError:
            print(f"\nError: Collection not found: {label}")

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

    def top_from_col(self, sample: str,
                     collections: list[str] = None,
                     top: int = 1,
                     look_around: int = -1
                     ) -> dict | None:
        """ Get the top x best matches
        :param sample: A string to match against one or more collections from this library.
        :param collections: A list of collection names to match against. If None uses all collections.
        :param top: The amount of best matches to return
        :param look_around: Set a limit to how many characters longer or shorter a (collection-) string may be before
               skipping it. Set to -1 for no limit.
        :return: A dictionary with results and some stats about the search.
        """
        # LBYL checks
        if sample.strip() == "" or sample is None:
            return None
        if type(sample) is not str:
            raise TypeError(f"'sample' argument is not a string: {sample}")
        if collections:
            if type(collections) is not list:
                raise TypeError(f"'collections' argument is not a list: {collections}")
            for collection in collections:
                if type(collection) is not str:
                    raise TypeError(f"'collections' argument list contains a non-string object: {collection}")
        else:
            collections = self.collections()
        if type(top) is not int:
            raise TypeError(f"'top' argument is not an integer: {top}")
        if top < 1:
            raise ValueError(f"'top' argument must be greater than 0: ({top} < 1)")
        if type(look_around) is not int:
            raise TypeError(f"'look_around' argument is not an integer: {look_around}")
        if look_around < -1:
            raise ValueError(f"'look_around' argument may not be smaller than -1: ({look_around} < -1)")

        results = {'sample': sample, 'skipped': 0, 'total': 0}
        st_t0 = perf_counter_ns()

        # do matching for each argumented collection
        temp_results = []
        for collection in collections:
            # apply collection pre-processing settings to sample
            if self.__strlib[collection]['ignore_case']:
                sample = sample.lower()
            if self.__strlib[collection]['to_ascii']:
                sample = normalize("NFKD", sample).encode("ascii", "ignore").decode()
            if not self.__strlib[collection]['no_strip']:
                sample = sample.strip()

            results['total'] += self.__strlib[collection]['num_ref']

            # do matching per word length
            len_sample = len(sample)
            for length, ref_list in self.__strlib[collection]['col_by_len'].items():
                # skip string set if character length is out of look_around range
                if look_around > -1:
                    if abs(length - len_sample) > look_around:
                        results['skipped'] += len(self.__strlib[collection]['col_by_len'][length])
                        continue

                # get a list ratios for this string set
                ratios = [ratio(sample, ref[2]) for ref in ref_list]

                # skim intermediate results to save time sorting
                for _ in range(min(top, len(ratios))):
                    idx = ratios.index(max(ratios))
                    result = (self.__strlib[collection]['col_by_len'][length][idx], ratios[idx]),
                    temp_results.extend(result)
                    ratios[idx] -= 1

        # finalize results and stats
        temp_results.sort(key=lambda x: x[1], reverse=True)
        results['results'] = temp_results[:top]
        results['collections'] = collections
        results['tested'] = results['total'] - results['skipped']
        results['time'] = round((perf_counter_ns() - st_t0) / 1e6)
        return results

