import fuzzy_matching as fm
from time import perf_counter_ns
from Levenshtein import ratio


def read_file(path: str) -> list[str]:
    with open(path) as file:  # encoding='utf-8'
        strings = file.readlines()
    return strings


if __name__ == '__main__':
    t1 = perf_counter_ns()
    geo = fm.StringLib()

    ## 10 strings
    custom = ['Timboektoe', ' \n', 'wehrwheg', 'Lutjebroek  ', 'Verweggistan', 'Neverland\n', 'Verwegië', ' irgendwo', '', ' ']
    geo.add_col(custom, 'cus', ignore_case=False, to_ascii=False, no_strip=True)
    ## 569 strings
    geo.add_col(read_file('.\\Testing\\landen - NL.txt'), 'co_nl', ignore_case=True, to_ascii=True, no_strip=False)
    geo.add_col(read_file('.\\Testing\\landen - FR.txt'), 'co_fr', ignore_case=True, to_ascii=True, no_strip=False)
    geo.add_col(read_file('.\\Testing\\landen - DE.txt'), 'co_de', ignore_case=True, to_ascii=True, no_strip=False)
    ## 61.000 strings
    # t0 = perf_counter_ns()

    lang = fm.StringLib()
    lang.add_col(read_file('.\\Testing\\uk-cities.txt'), 'ci_uk', ignore_case=True, to_ascii=True, no_strip=False)  # 168/140/40 ms
    # print(f"Add 'ci_uk' collection to library took: {round((perf_counter_ns() - t0) / 1e6)} ms")
    ## 200.000 strings
    # t0 = perf_counter_ns()
    lang.add_col(read_file('.\\Testing\\basiswoorden-gekeurd.txt'), 'wo_nl', ignore_case=True, to_ascii=True, no_strip=False)  # 701/555/180/135 ms
    # print(f"Add 'wo_nl' collection to library took: {round((perf_counter_ns() - t0) / 1e6)} ms")
    ## 336.000 strings
    # t0 = perf_counter_ns()
    lang.add_col(read_file('.\\Testing\\words_fr.txt'), 'wo_fr', ignore_case=True, to_ascii=True, no_strip=False)
    # print(f"Add 'wo_fr' collection to library took: {round((perf_counter_ns() - t0) / 1e6)} ms")
    ## 466.000 strings
    # t0 = perf_counter_ns()
    lang.add_col(read_file('.\\Testing\\words_eng.txt'), 'wo_uk', ignore_case=True, to_ascii=True, no_strip=False)  # 2080/1345/510/310 ms
    # print(f"Add 'wo_uk' collection to library took: {round((perf_counter_ns() - t0) / 1e6)} ms")
    print(f"Add all collections to library took: {round((perf_counter_ns() - t1) / 1e6)} ms")  # 740

    # geo.del_col('co_fr')
    # geo.ren_col('co_fr', 'landen-frans')
    # print(geo.col_info('cus', full=True))
    # print(lang)
    # print(lang.collections())
    # geo.clr_lib()
    # for key, value in geo.lib_info().items():
    #     print(f"\t{key}: {value}")
    # print()


    # set_opt method for changing a collections' options


    # test = geo.top_from_col('  lAagdën ', top=15, look_around=5)
    # test = lang.top_from_col('londo', ['ci_uk', 'wo_nl'], top=5, look_around=5)  # 72/60 ms
    # test = lang.top_from_col('akwisietie', ['ci_uk', 'wo_nl'], top=5, look_around=3)  # 110/115 ms
    # test = lang.top_from_col('  Vërderwegdanallesanderszz ', top=5, look_around=-1)  # 600 ms
    test = lang.top_from_col('jastifikaition', ['wo_uk'], top=5, look_around=5)  # 400/155 ms

    if test:
        print(f"\nTop {len(test['results'])} results found:")
        for i, result in enumerate(test['results']):
            print(f"{i + 1}. {result[0][0]}    (from: '{result[0][1]}', as: '{result[0][2]}', ratio: '{result[1]}')")
        print((f"\n< Tested '{test['sample']}' against {test['tested']} references out of {test['total']}"
               f" total in collections {test['collections']} (skipped {test['skipped']}) in {test['time']} ms >"))


