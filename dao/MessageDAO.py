import psycopg2
from config.dbconfig import pg_config

class MessageDAO:
    def __init__(self):
        connection_url = "dbname=%s user=%s password=%s host=%s port=%s" % (pg_config['dbname'], pg_config['user'], pg_config['password'], pg_config['host'], pg_config['port'])
        self.conn = psycopg2.connect(connection_url)

    def postmessage(self, cid, uid, text):
        cursor = self.conn.cursor()                        #chat id, user id   message format '{messages goes here}'
        query = 'insert into message(cid, uid, time, text) values (%s, %s, CURRENT_TIMESTAMP, %s) returning  mid;'
        cursor.execute(query, (cid, uid, text, ))
        result = cursor.fetchone()[0]
        self.conn.commit()
        return result

    def postHashtag(self, hashtext):
        cursor = self.conn.cursor()
        query = 'insert into hashtag(hashname) values(%s) returning hid;'
        cursor.execute(query, (hashtext, ))
        result = cursor.fetchone()[0]
        self.conn.commit()
        return result

    def insertHasHash(self, m, hid):
        cursor = self.conn.cursor()
        query = 'insert into containhash values(%s, %s);'
        cursor.execute(query, (hid, m))
        self.conn.commit()
        return "Done"

    def searchHashInChatmsg(self, cid, hashname):
        cursor = self.conn.cursor()
        query = 'select username, hashname, cid, mid, uid, text from "user" natural inner join message natural inner join containhash natural inner join hashtag natural inner join chat where cid=%s and hashname=%s;'
        cursor.execute(query, (cid, hashname))
        result = []
        for m in cursor:
            result.append(m)
        return result

    def allMessages(self):
        cursor = self.conn.cursor()
        query = 'select  mid, text, chatname, time, username from chat natural inner join message natural inner join "user";'
        cursor.execute(query)
        return cursor

    def messageById(self, mid):
        cursor = self.conn.cursor()
        query = 'select mid, text, chatname, time, username  from chat natural inner join message natural inner join "user" where mid=%s;'
        cursor.execute(query, (mid, ))
        result = []
        for m in cursor:
            result.append(m)
        return result

    def hashtagList(self):
        cursor = self.conn.cursor()
        query = 'select array_agg(hashname), array_agg(hid) from hashtag;'
        cursor.execute(query)
        result = cursor.fetchone()
        self.conn.commit()
        print(result)
        return result


    def messagesFromChat(self, cid):
        cursor = self.conn.cursor()
        query = 'with likes as (select count(uid) as likes, array_agg(u.username) as likeby, mid from "like" natural inner join "user" as u group by mid), dislikes as (select count(uid) as dislikes, array_agg(u.username) as dislikeby, mid from dislike natural inner join "user" as u group by mid), replies as (select message.text as rtext, reply.reply as reply, reply.mid as mid from reply natural inner join message) select distinct u.username, m.mid, time, text, likes.likeby, dislikes.dislikeby, replies.rtext, coalesce(likes.likes, 0) as likes, coalesce(dislikes.dislikes, 0) as dislikes, coalesce(replies.mid, 0) as replyid from chat as c natural inner join message as m natural inner join "user" as u left join dislikes on (m.mid = dislikes.mid) left join likes on (m.mid = likes.mid) left join replies on (m.mid = replies.reply) where c.cid=%s group by likes.likes, dislikes.dislikes, u.username, m.mid, likes.likeby, dislikes.dislikeby, replies.rtext, replies.mid order by time; '
        result = []
        cursor.execute(query, (cid, ))
        for m in cursor:
            result.append(m)
        return result

    #original one
    def messagesFromChatwith(self, cid):
        cursor = self.conn.cursor()
        query = 'select username, mid, time, text  from chat natural inner join message natural inner join "user" where cid=%s;'
        result = []
        cursor.execute(query, (cid, ))
        for m in cursor:
            result.append(m)
        return result

    def messagesFromUser(self, uid):
        cursor = self.conn.cursor()
        query = 'select chatname, cid, mid, time, text  from chat natural inner join message natural inner join "user" where uid=%s;'
        result = []
        cursor.execute(query, (uid, ) )
        for m in cursor:
            result.append(m)
        return result

    def messageReply(self, mid):
        cursor = self.conn.cursor()
        query = 'select m2.text, u.username  from message as m1, reply as r, message as m2, "user" as u where u.uid=m2.uid and m1.mid=r.mid and m2.mid=r.reply and m1.mid=%s;'
        result = []
        cursor.execute(query, (mid, ))
        for m in cursor:
            result.append(m)
        return result

    def countRepliesMessage(self, mid):
        cursor = self.conn.cursor()
        query = 'select count(*) from message as m1, reply as r, message as m2, "user" as u where u.uid=m2.uid and m1.mid=r.mid and m2.mid=r.reply and m1.mid=%s;'
        cursor.execute(query, (mid, ))
        return cursor.fetchone()[0]

    def getLikes(self):
        cursor = self.conn.cursor()
        query = 'select mid, username from "like" natural inner join "user";'
        result = []
        cursor.execute(query)
        for m in cursor:
            result.append(m)
        return result

    def messageLikes(self, mid):
        cursor = self.conn.cursor()
        query = 'select username from message as m, "like" as l, "user" as u where m.mid=l.mid and u.uid=l.uid and m.mid=%s;'
        result = []
        cursor.execute(query, (mid, ))
        for m in cursor:
            result.append(m)
        return result

    def getDislikes(self):
        cursor = self.conn.cursor()
        query = 'select mid, username from "user" natural inner join dislike;'
        result = []
        cursor.execute(query)
        for m in cursor:
            result.append(m)
        return result

    def messagesDislikes(self, mid):
        cursor = self.conn.cursor()
        query = 'select username from message as m, dislike as d, "user" as u where m.mid=d.mid and u.uid=d.uid and m.mid=%s;'
        result = []
        cursor.execute(query, (mid, ))
        for m in cursor:
            result.append(m)
        return result

    def countLikesMessage(self, mid):
        cursor = self.conn.cursor()
        query = 'select count(*) from message as m, "like" as l, "user" as u where m.mid=l.mid and u.uid=l.uid and m.mid=%s;'
        cursor.execute(query, (mid, ))
        return cursor.fetchone()[0]

    def countDislikesMessage(self, mid):
        cursor = self.conn.cursor()
        query = 'select count(*) from message as m, dislike as d, "user" as u where m.mid=d.mid and u.uid=d.uid and m.mid=%s;'
        cursor.execute(query, (mid, ))
        return cursor.fetchone()[0]

    def insertlike(self, uid, mid):
        cursor = self.conn.cursor()
        query = 'insert into "like" values (%s, %s)'
        cursor.execute(query, (uid, mid))
        self.conn.commit()
        return "Done"

    def insertdislike(self, uid, mid):
        cursor = self.conn.cursor()
        query = 'insert into dislike values (%s, %s)'
        cursor.execute(query, (uid, mid))
        self.conn.commit()
        return "Done"

    def insertreply(self, mid, reply):
        cursor = self.conn.cursor()
        query = 'insert into reply values (%s, %s)'
        cursor.execute(query, (mid, reply))
        self.conn.commit()
        return "Done"
