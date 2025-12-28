# app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime

app = Flask(__name__)

# --- 数据库配置 ---
# !!! 请将 'your_mysql_password' 替换为你的真实 MySQL 密码 !!!
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '114514'
app.config['MYSQL_DB'] = 'hltv'

# --- Flask 配置 ---
app.secret_key = 'your_very_secret_key'  # 用于 flash 消息，保持不变即可

mysql = MySQL(app)


# --- 主页/仪表盘 ---
# --- 主页/仪表盘 ---
@app.route('/')
def index():
    """主页，展示队伍排名和数据概览"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # 1. 获取队伍排名 (这部分保持不变)
    cursor.execute('SELECT * FROM team ORDER BY point DESC')
    teams_ranking = cursor.fetchall()

    # 2. 【修改】查询所有选手的平均Rating，并按Rating降序排名
    # 我们从 player_match_stat 表中计算每个选手的平均Rating
    rating_query = """
                   SELECT p.pid, p.pname, t.tname, AVG(pms.rating) as avg_rating
                   FROM player p
                            JOIN player_match_stat pms ON p.pid = pms.pid
                            JOIN team t ON p.tid = t.tid
                   GROUP BY p.pid, p.pname, t.tname
                   ORDER BY avg_rating DESC LIMIT 10; -- 限制只显示前10名
                   """
    cursor.execute(rating_query)
    top_players_by_rating = cursor.fetchall()

    cursor.close()

    # 3. 将新的数据传递给模板
    return render_template('index.html',
                           teams_ranking=teams_ranking,
                           top_players_by_rating=top_players_by_rating)  # 变量名已更改

# --- 队伍管理 CRUD ---
@app.route('/teams')
def list_teams():
    """显示所有队伍列表"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM team ORDER BY tid')
    teams = cursor.fetchall()
    cursor.close()
    return render_template('teams.html', teams=teams)


@app.route('/teams/add', methods=['POST'])
def add_team():
    """添加新队伍"""
    if request.method == 'POST':
        tname = request.form['tname']
        logo_url = request.form['logo_url']
        point = request.form['point']

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO team (tname, logo_url, point) VALUES (%s, %s, %s)', (tname, logo_url, point))
        mysql.connection.commit()
        cursor.close()
        flash('队伍添加成功！')
    return redirect(url_for('list_teams'))


@app.route('/teams/edit/<int:tid>', methods=['GET', 'POST'])
def edit_team(tid):
    """编辑队伍信息"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        tname = request.form['tname']
        logo_url = request.form['logo_url']
        point = request.form['point']
        cursor.execute('UPDATE team SET tname=%s, logo_url=%s, point=%s WHERE tid=%s', (tname, logo_url, point, tid))
        mysql.connection.commit()
        cursor.close()
        flash('队伍更新成功！')
        return redirect(url_for('list_teams'))

    cursor.execute('SELECT * FROM team WHERE tid = %s', (tid,))
    team_to_edit = cursor.fetchone()
    cursor.close()
    return render_template('teams.html', team_to_edit=team_to_edit)


@app.route('/teams/delete/<int:tid>', methods=['POST'])
def delete_team(tid):
    """删除队伍"""
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM team WHERE tid = %s', (tid,))
    mysql.connection.commit()
    cursor.close()
    flash('队伍删除成功！')
    return redirect(url_for('list_teams'))


# --- 队伍详情页 ---
@app.route('/teams/<int:tid>')
def team_detail(tid):
    """显示单个队伍的详情和其队员"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute('SELECT * FROM team WHERE tid = %s', (tid,))
    team = cursor.fetchone()
    if not team:
        flash('未找到指定的队伍！')
        return redirect(url_for('list_teams'))

    cursor.execute('SELECT * FROM player WHERE tid = %s ORDER BY pname', (tid,))
    players = cursor.fetchall()

    cursor.close()
    return render_template('team_detail.html', team=team, players=players)


# --- 选手管理 CRUD ---
# app.py

# ... (其他代码) ...

@app.route('/players')
def list_players():
    """显示所有选手列表"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # 1. 查询所有队伍，用于“添加选手”表单的下拉框
    cursor.execute('SELECT tid, tname FROM team ORDER BY tname')
    all_teams = cursor.fetchall()

    # 2. 查询所有选手及其所属队伍名称
    cursor.execute('SELECT p.*, t.tname FROM player p JOIN team t ON p.tid = t.tid ORDER BY p.pid')
    players = cursor.fetchall()

    cursor.close()

    # 3. 将两个列表都传递给模板
    return render_template('players.html', players=players, all_teams=all_teams)


# ... (其他代码) ...

@app.route('/players/add', methods=['POST'])
def add_player():
    """添加新选手"""
    if request.method == 'POST':
        tid = request.form['tid']
        pname = request.form['pname']
        country = request.form['country']
        photo_url = request.form['photo_url']
        player_rating = request.form['player_rating']

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO player (tid, pname, country, photo_url, player_rating) VALUES (%s, %s, %s, %s, %s)',
                       (tid, pname, country, photo_url, player_rating))
        mysql.connection.commit()
        cursor.close()
        flash('选手添加成功！')
    return redirect(url_for('list_players'))


@app.route('/players/edit/<int:pid>', methods=['GET', 'POST'])
def edit_player(pid):
    """编辑选手信息"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute('SELECT tid, tname FROM team ORDER BY tname')
    all_teams = cursor.fetchall()

    if request.method == 'POST':
        tid = request.form['tid']
        pname = request.form['pname']
        country = request.form['country']
        photo_url = request.form['photo_url']
        player_rating = request.form['player_rating']
        cursor.execute('UPDATE player SET tid=%s, pname=%s, country=%s, photo_url=%s, player_rating=%s WHERE pid=%s',
                       (tid, pname, country, photo_url, player_rating, pid))
        mysql.connection.commit()
        cursor.close()
        flash('选手更新成功！')
        return redirect(url_for('list_players'))

    cursor.execute('SELECT * FROM player WHERE pid = %s', (pid,))
    player_to_edit = cursor.fetchone()
    cursor.close()
    return render_template('players.html', player_to_edit=player_to_edit, all_teams=all_teams)


@app.route('/players/delete/<int:pid>', methods=['POST'])
def delete_player(pid):
    """删除选手"""
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM player WHERE pid = %s', (pid,))
    mysql.connection.commit()
    cursor.close()
    flash('选手删除成功！')
    return redirect(url_for('list_players'))


# --- 选手详情页 ---
@app.route('/players/<int:pid>')
def player_detail(pid):
    """显示单个选手的详情和其参与的比赛"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute('SELECT p.*, t.tname FROM player p JOIN team t ON p.tid = t.tid WHERE p.pid = %s', (pid,))
    player = cursor.fetchone()
    if not player:
        flash('未找到指定的选手！')
        return redirect(url_for('list_players'))

    matches_query = """
                    SELECT DISTINCT m.match_id, \
                                    m.match_time, \
                                    m.match_stage, \
                                    t1.tname as team1_name, \
                                    t2.tname as team2_name
                    FROM player_match_stat pms
                             JOIN match_stat ms ON pms.stat_id = ms.stat_id
                             JOIN `match` m ON ms.match_id = m.match_id
                             JOIN team t1 ON m.tid1 = t1.tid
                             JOIN team t2 ON m.tid2 = t2.tid
                    WHERE pms.pid = %s \
                    ORDER BY m.match_time DESC; \
                    """
    cursor.execute(matches_query, (pid,))
    matches = cursor.fetchall()

    cursor.close()
    return render_template('player_detail.html', player=player, matches=matches)


# --- 比赛详情页 ---
@app.route('/matches/<int:match_id>')
def match_detail(match_id):
    """显示单场比赛的详情和所有选手数据"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    match_query = """
                  SELECT m.*, t1.tname as team1_name, t2.tname as team2_name, tor.tournament_name
                  FROM `match` m
                           JOIN team t1 ON m.tid1 = t1.tid
                           JOIN team t2 ON m.tid2 = t2.tid
                           JOIN tournament tor ON m.tournament_id = tor.tournament_id
                  WHERE m.match_id = %s; \
                  """
    cursor.execute(match_query, (match_id,))
    match = cursor.fetchone()
    if not match:
        flash('未找到指定的比赛！')
        return redirect(url_for('index'))

    stats_query = """
                  SELECT p.pid, \
                         p.pname, \
                         t.tname           as team_name,
                         SUM(pms.kill)     as total_kills, \
                         SUM(pms.death)    as total_deaths,
                         SUM(pms.assist)   as total_assists, \
                         SUM(pms.headshot) as total_headshots,
                         AVG(pms.kd)       as avg_kd, \
                         AVG(pms.adr)      as avg_adr, \
                         AVG(pms.rating)   as avg_rating
                  FROM player_match_stat pms
                           JOIN match_stat ms ON pms.stat_id = ms.stat_id
                           JOIN player p ON pms.pid = p.pid
                           JOIN team t ON p.tid = t.tid
                  WHERE ms.match_id = %s
                  GROUP BY p.pid, p.pname, t.tname \
                  ORDER BY avg_rating DESC; \
                  """
    cursor.execute(stats_query, (match_id,))
    player_stats = cursor.fetchall()

    cursor.close()
    return render_template('match_detail.html', match=match, player_stats=player_stats)


@app.route('/matches_manage')
def matches_manage():
    """比赛管理主页，显示所有比赛"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = """
            SELECT m.match_id, \
                   m.match_time, \
                   m.match_stage, \
                   m.team1_point, \
                   m.team2_point,
                   t1.tname as team1_name, \
                   t2.tname as team2_name, \
                   tor.tournament_name
            FROM `match` m
                     JOIN team t1 ON m.tid1 = t1.tid
                     JOIN team t2 ON m.tid2 = t2.tid
                     JOIN tournament tor ON m.tournament_id = tor.tournament_id
            ORDER BY m.match_time DESC; \
            """
    cursor.execute(query)
    all_matches = cursor.fetchall()
    cursor.close()
    return render_template('matches_manage.html', matches=all_matches)


@app.route('/match_create/step1', methods=['GET', 'POST'])
def match_create_step1():
    """创建比赛 - 步骤1：填写基本信息"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # 获取所有赛事和队伍，用于下拉框
    cursor.execute('SELECT * FROM tournament ORDER BY tournament_id DESC')
    tournaments = cursor.fetchall()
    cursor.execute('SELECT * FROM team ORDER BY tname')
    teams = cursor.fetchall()

    if request.method == 'POST':
        # 从表单获取数据
        tournament_id = request.form['tournament_id']
        tid1 = request.form['tid1']
        tid2 = request.form['tid2']
        match_stage = request.form['match_stage']
        match_time = request.form['match_time']
        map_name = request.form['map_name']
        # 验证对阵双方不能相同
        if tid1 == tid2:
            flash('对阵双方不能是同一支队伍！')
        else:
            # 将步骤1的数据存入 session，以便在步骤2中使用
            session['match_data'] = {
                'tournament_id': tournament_id,
                'tid1': tid1,
                'tid2': tid2,
                'match_stage': match_stage,
                'match_time': match_time,
                'map_name': map_name
            }
            return redirect(url_for('match_create_step2'))

    cursor.close()
    return render_template('match_create_step1.html', tournaments=tournaments, teams=teams)


@app.route('/match_create/step2', methods=['GET', 'POST'])
def match_create_step2():
    """创建比赛 - 步骤2：选择参赛选手"""
    # 检查 session 中是否有步骤1的数据
    if 'match_data' not in session:
        flash('请先完成第一步！')
        return redirect(url_for('match_create_step1'))

    match_data = session['match_data']
    tid1 = match_data['tid1']
    tid2 = match_data['tid2']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # 获取两队的所有选手
    cursor.execute('SELECT * FROM player WHERE tid = %s ORDER BY pname', (tid1,))
    players_team1 = cursor.fetchall()
    cursor.execute('SELECT * FROM player WHERE tid = %s ORDER BY pname', (tid2,))
    players_team2 = cursor.fetchall()

    # 获取队伍名称，用于显示
    cursor.execute('SELECT tname FROM team WHERE tid = %s', (tid1,))
    team1_name = cursor.fetchone()['tname']
    cursor.execute('SELECT tname FROM team WHERE tid = %s', (tid2,))
    team2_name = cursor.fetchone()['tname']

    if request.method == 'POST':
        # 获取所有被选中的选手ID
        selected_player_ids = request.form.getlist('selected_players')

        if not selected_player_ids:
            flash('请至少选择一名选手！')
        else:
            # 将选中的选手ID存入 session
            session['selected_player_ids'] = selected_player_ids
            return redirect(url_for('match_create_step3'))

    cursor.close()
    return render_template('match_create_step2.html',
                           players_team1=players_team1,
                           players_team2=players_team2,
                           team1_name=team1_name,
                           team2_name=team2_name)


# app.py

# ... (其他代码) ...

@app.route('/match_create/step3', methods=['GET', 'POST'])
def match_create_step3():
    """创建比赛 - 步骤3：录入选手数据并提交"""
    # 检查 session 数据是否完整
    if 'match_data' not in session or 'selected_player_ids' not in session:
        flash('操作流程不完整，请从头开始！')
        return redirect(url_for('match_create_step1'))

    match_data = session['match_data']
    selected_player_ids = session['selected_player_ids']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # 获取所有选中选手的详细信息
    placeholders = ', '.join(['%s'] * len(selected_player_ids))
    query = f"SELECT * FROM player WHERE pid IN ({placeholders})"
    cursor.execute(query, tuple(selected_player_ids))
    players_to_enter_data = cursor.fetchall()

    if request.method == 'POST':
        try:
            # --- 开始数据库事务 ---
            mysql.connection.autocommit(False)

            # 1. 插入 `match` 表
            cursor.execute(
                "INSERT INTO `match` (tournament_id, tid1, tid2, match_stage, match_time) VALUES (%s, %s, %s, %s, %s)",
                (match_data['tournament_id'], match_data['tid1'], match_data['tid2'], match_data['match_stage'],
                 match_data['match_time'])
            )
            new_match_id = cursor.lastrowid
            print(f"[调试] 成功创建 match，ID: {new_match_id}")  # <--- 调试点 1

            # 2. 插入 `match_stat` 表
            # ↓↓↓ 关键调试信息 ↓↓↓
            print(
                f"[调试] 准备创建 match_stat，match_id: {new_match_id}, map_name: '{match_data.get('map_name', 'NOT FOUND')}'")
            # ↑↑↑ 关键调试信息 ↑↑↑
            cursor.execute("INSERT INTO match_stat (match_id, map_name) VALUES (%s, %s)",
                           (new_match_id, match_data['map_name']))
            new_stat_id = cursor.lastrowid
            print(f"[调试] 成功创建 match_stat，ID: {new_stat_id}")  # <--- 调试点 2

            team1_total_kills = 0
            team2_total_kills = 0

            # 3. 遍历所有选手，插入 `player_match_stat` 表
            for player in players_to_enter_data:
                pid = player['pid']
                kill = int(request.form.get(f'kill_{pid}', 0))
                death = int(request.form.get(f'death_{pid}', 0))
                assist = int(request.form.get(f'assist_{pid}', 0))
                headshot = int(request.form.get(f'headshot_{pid}', 0))
                kd = round(kill / death, 2) if death > 0 else kill
                adr = float(request.form.get(f'adr_{pid}', 0.0))
                rating = float(request.form.get(f'rating_{pid}', 0.0))

                # ↓↓↓ 循环内的调试信息 ↓↓↓
                print(f"[调试] 准备为选手 {player['pname']} (PID: {pid}) 插入数据。K/D/A: {kill}/{death}/{assist}")
                # ↑↑↑ 循环内的调试信息 ↑↑↑

                cursor.execute(
                    "INSERT INTO player_match_stat (stat_id, pid, `kill`, death, assist, headshot, kd, adr, rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (new_stat_id, pid, kill, death, assist, headshot, kd, adr, rating)
                )

                # 累加队伍总击杀
                if str(player['tid']) == match_data['tid1']:
                    team1_total_kills += kill
                else:
                    team2_total_kills += kill

            # 4. 更新 `match` 表中的队伍总击杀
            cursor.execute(
                "UPDATE `match` SET team1_point = %s, team2_point = %s WHERE match_id = %s",
                (team1_total_kills, team2_total_kills, new_match_id)
            )
            print(f"[调试] 成功更新 match 总分。Team1: {team1_total_kills}, Team2: {team2_total_kills}")  # <--- 调试点 3

            # --- 提交事务 ---
            mysql.connection.commit()
            flash('比赛数据创建成功！')

        except Exception as e:
            # --- 如果出错，回滚事务 ---
            mysql.connection.rollback()
            print(f"[错误] 事务失败并回滚，原始错误: {e}")  # <--- 调试点 4 (最重要！)
            flash(f'创建失败：{str(e)}')
        finally:
            # 清理 session
            session.pop('match_data', None)
            session.pop('selected_player_ids', None)
            cursor.close()
            mysql.connection.autocommit(True)  # 恢复自动提交
            return redirect(url_for('matches_manage'))

    cursor.close()
    return render_template('match_create_step3.html', players=players_to_enter_data)

# ==================== 结束：比赛管理功能 ====================

# app.py

# ... (您已有的所有代码) ...

# ==================== 新增：赛事管理功能 ====================

@app.route('/tournaments_manage')
def tournaments_manage():
    """赛事管理主页，显示所有赛事"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM tournament ORDER BY tournament_id DESC")
    all_tournaments = cursor.fetchall()
    cursor.close()
    return render_template('tournaments_manage.html', tournaments=all_tournaments)


# app.py

# ... (其他代码) ...

@app.route('/tournament_add', methods=['GET', 'POST'])
def tournament_add():
    """添加新赛事"""
    if request.method == 'POST':
        tournament_name = request.form['tournament_name']
        status = request.form['status']
        start_time = request.form['start_time']

        # ↓↓↓ 新增：获取结束时间 ↓↓↓
        end_time = request.form['end_time']
        # ↑↑↑ 新增：获取结束时间 ↑↑↑

        cursor = mysql.connection.cursor()
        try:
            # ↓↓↓ 修改：在 INSERT 语句中加入 end_time ↓↓↓
            cursor.execute(
                "INSERT INTO tournament (tournament_name, start_time, end_time, status) VALUES (%s, %s, %s, %s)",
                (tournament_name, start_time, end_time, status)
            )
            # ↑↑↑ 修改：在 INSERT 语句中加入 end_time ↑↑↑

            mysql.connection.commit()
            flash('新赛事添加成功！')
            return redirect(url_for('tournaments_manage'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'添加失败：{str(e)}')
        finally:
            cursor.close()

    return render_template('tournament_add.html')


# ... (其他代码) ...

# ==================== 结束：赛事管理功能 ====================

if __name__ == '__main__':
    app.run(debug=True)
if __name__ == '__main__':
    app.run(debug=True)
