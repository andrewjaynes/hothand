import pandas as pd, numpy as np, sys
src, out = sys.argv[1], sys.argv[2]
p = pd.read_parquet(src + '/mbb/pbp/parquet/play_by_play_2026.parquet')
p = p[((p.home_team_id == 150) | (p.away_team_id == 150))]
fg = p[(p.team_id == 150) & p.type_text.isin(['JumpShot','LayUpShot','DunkShot','TipShot'])].copy()
fg['opponent'] = np.where(fg.home_team_id == 150, fg.away_team_name, fg.home_team_name)
fg['home'] = fg.home_team_id == 150
fg['made'] = fg.scoring_play.astype(int)
fg['three'] = (fg.score_value == 3).astype(int)
fg['game_play_number'] = fg.game_play_number.astype(int)
fg = fg.sort_values(['game_date_time','game_id','game_play_number'])
fg['shot_num_in_game'] = fg.groupby('game_id').cumcount() + 1
fg['player_shot_num_in_game'] = fg.groupby(['game_id','athlete_id_1']).cumcount() + 1
cols = dict(game_id='game_id', game_date='date', opponent='opponent', home='home', season_type='season_type',
            game_play_number='play_number', period_number='half', clock_display_value='clock',
            start_game_seconds_remaining='game_seconds_remaining', athlete_id_1='player_id', athlete_name_1='player',
            type_text='shot_type', three='three_pointer', made='made', coordinate_x='x', coordinate_y='y',
            shot_num_in_game='team_shot_num_in_game', player_shot_num_in_game='player_shot_num_in_game', text='description')
fg = fg[list(cols)].rename(columns=cols)
fg['player_id'] = fg.player_id.astype('Int64')
fg.to_csv(out, index=False)
print(len(fg), 'Duke FGA;', fg.made.mean().round(3), 'FG%')
print(fg.player.isna().sum(), 'missing shooter')
