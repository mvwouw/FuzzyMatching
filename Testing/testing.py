import fuzzy_matching as fm
from time import perf_counter_ns


def read_file(path: str) -> list[str]:
    # t2 = perf_counter_ns()
    with open(path) as file:  # encoding='utf-8'
        strings = file.readlines()
    # print(f"Read file to list took: {round((perf_counter_ns() - t2) / 1e6)} ms")
    return strings


def read_file_todict(path: str) -> dict:
    # quick and dirty creating a dict with references and relations
    # t2 = perf_counter_ns()
    with open(path) as file:  # encoding='utf-8'
        rrdict = {}
        for line in file.readlines():
            ref_rel = line.split('*')
            rrdict[ref_rel[0]] = ref_rel[1].strip()
    # print(f"Read file to dict took: {round((perf_counter_ns() - t2) / 1e6)} ms")
    return rrdict


if __name__ == '__main__':
    t1 = perf_counter_ns()
    # geo = fm.StringLib()

    ## 10 strings
    # custom = ['Timboektoe', ' \n', 'wehrwheg', 'Lutjebroek  ', 'Verweggistan', 'Neverland\n', 'Verwegië', ' irgendwo', '', ' ']
    # geo.add_col(custom, 'cus', ignore_case=False, to_ascii=False, no_strip=True)
    ## 569 strings
    # geo.add_col(read_file('.\\Testing\\landen - NL.txt'), 'co_nl', ignore_case=True, to_ascii=True, no_strip=False)
    # geo.add_col(read_file('.\\Testing\\landen - FR.txt'), 'co_fr', ignore_case=True, to_ascii=True, no_strip=False)
    # geo.add_col(read_file('.\\Testing\\landen - DE.txt'), 'co_de', ignore_case=True, to_ascii=True, no_strip=False)
    ## 61.000 strings
    # t0 = perf_counter_ns()

    lang = fm.StringLib()
    # lang.add_col(read_file('.\\Testing\\uk-cities.txt'), 'ci_uk', ignore_case=True, to_ascii=True, no_strip=False)  # 168/140/50 ms
    lang.add_col(read_file_todict('.\\Testing\\uk-cities_link.txt'), 'ci_uk', ignore_case=True, to_ascii=True, no_strip=False)  # 75 ms
    # print(f"Add 'ci_uk' collection to library took: {round((perf_counter_ns() - t0) / 1e6)} ms")
    ## 200.000 strings
    # t0 = perf_counter_ns()
    # lang.add_col(read_file('.\\Testing\\basiswoorden-gekeurd.txt'), 'wo_nl', ignore_case=True, to_ascii=True, no_strip=False)  # 701/555/180/135 ms
    lang.add_col(read_file_todict('.\\Testing\\basiswoorden-gekeurd_link.txt'), 'wo_nl', ignore_case=True, to_ascii=True, no_strip=False)  # 285 ms
    # print(f"Add 'wo_nl' collection to library took: {round((perf_counter_ns() - t0) / 1e6)} ms")
    ## 336.000 strings
    # t0 = perf_counter_ns()
    lang.add_col(read_file('.\\Testing\\words_fr.txt'), 'wo_fr', ignore_case=True, to_ascii=True, no_strip=False)
    # print(f"Add 'wo_fr' collection to library took: {round((perf_counter_ns() - t0) / 1e6)} ms")
    ## 466.000 strings
    # t0 = perf_counter_ns()
    lang.add_col(read_file('.\\Testing\\words_eng.txt'), 'wo_uk', ignore_case=True, to_ascii=True, no_strip=False)  # 2080/1345/510/310 ms
    # print(f"Add 'wo_uk' collection to library took: {round((perf_counter_ns() - t0) / 1e6)} ms")
    print(f"Add all collections to library took: {round((perf_counter_ns() - t1) / 1e6)} ms")  # 740/795 ms

    # geo.del_col('co_fr')
    # geo.ren_col('co_fr', 'landen-frans')
    # print(geo.col_info('cus', full=True))
    # geo.set_pre_opt('cus', ignore_case=False, to_ascii=False, no_strip=False)
    # print(geo.col_info('cus', full=True))
    # print(lang)
    # print(lang.collections())
    # geo.clr_lib()
    # for key, value in geo.lib_info().items():
    #     print(f"\t{key}: {value}")
    # print()


    # test = geo.get_top('  lAagdën ', top=0)
    # test = lang.get_top('Londen', ['ci_uk'], top=5, look_around=5, lmin=3)  # 72/60/50 ms
    # test = lang.get_top('akwisietie', ['ci_uk', 'wo_nl'], top=5, look_around=3, lmin=3)  # 110/115/80 ms
    test = lang.get_top('  Vërderwegdanallesanderszz ', top=5, look_around=-1, lmin=3)  # 600/515 ms
    # test = lang.get_top('jastifikaition', ['wo_uk'], top=5, look_around=5, lmin=3, lmax=0)  # 400/155/135 ms

    if test:
        print(f"\nTop {len(test['results'])} results:")
        for i, result in enumerate(test['results']):
            print(f"{i + 1}. {result[0][0]}    (from: '{result[0][1]}', as: '{result[0][2]}', ratio: '{round(result[1], 2)}', relation: '{result[0][3]}')")
        print((f"\n< Tested '{test['query']}' against {test['tested']} references out of {test['total']}"
               f" total in collections {test['collections']} (skipped {test['skipped']}) in {test['time']} ms >"))


