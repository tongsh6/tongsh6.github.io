---
layout: post
title: "Oracle sql语句练习"
date: 2013-01-23 19:56:51 +0800
last_modified_at: "2022-10-26 17:32:00 +0800"
categories: [技术]
tags: [oracle, Oracle, ORACLE, 查询]
source: "csdn"
csdn_id: "8535523"
source_url: "https://blog.csdn.net/tongsh6/article/details/8535523"
---

在网上找的Oracle sql语句练习  

终于磕磕绊绊的做完了！！！！  

## 1、查询“c001”课程比“c002”课程成绩高的所有学生的学号；  

```sql  

select x.sno  

from  

  (select \* from sc where cno='c001'  

  )x,  

  (select \* from sc where cno='c002'  

  )y  

where x.score>y.score  

and x.sno    =y.sno;  

```

## 2、查询平均成绩大于60 分的同学的学号和平均成绩；  

```sql  

select sno,  

  avg(score)  

from sc  

group by sno  

having avg(score)>60  

order by avg(score);  

```  

## 3、查询所有同学的学号、姓名、选课数、总成绩；  

```sql  

select s1.sno,  

  s1.sname,  

  s2.c,  

  s2.s  

from student s1,  

  (select sno, count(cno) c,sum(score) s from sc group by sno  

  )s2  

where s1.sno=s2.sno;  

```  

## 4、查询姓“刘”的老师的个数；  

```sql  

select tname,  

  count(\*)  

from teacher  

where tname like('刘%')  

group by tname;  

```  

## 5、查询没学过“谌燕”老师课的同学的学号、姓名；  

```sql  

select s1.sno  

from sc s1,  

  (select cno  

  from course t1,  

    (select distinct tno from teacher where tname='谌燕'  

    )t2  

  where t1.tno!=t2.tno  

  )s2  

where s1.cno=s2.cno;  

select a.sno,  

  a.sname  

from student a  

where a.sno not in  

  (select distinct s.sno  

  from sc s,  

    (select c.\*  

    from course c ,  

      (select tno from teacher t where tname='谌燕'  

      )t  

    where c.tno=t.tno  

    ) b  

  where s.cno = b.cno  

  )  

```  

## 6、查询学过“c001”并且也学过编号“c002”课程的同学的学号、姓名；  

```sql  

select \*  

from student  

where sno in  

  (select DISTINCT sno from sc where cno in ('c001','c002')  

  );  

```  

## 7、查询学过“谌燕”老师所教的所有课的同学的学号、姓名；  

```sql  

select \*  

from student  

where sno in  

  (select DISTINCT s3.sno  

  from sc s3,  

    (select distinct s1.cno  

    from course s1,  

      (select tno from teacher where tname='谌燕'  

      )s2  

    where s1.tno=s2.tno  

    )s4  

  where s4.cno=s3.cno  

  );  

select distinct st.\*  

from student st  

join sc s  

on st.sno=s.sno  

join course c  

on s.cno=c.cno  

join teacher t  

on c.tno     =t.tno  

where t.tname='谌燕'  

```  

## 8、查询课程编号“c002”的成绩比课程编号“c001”课程低的所有同学的学号、姓名；  

```sql  

select \*  

from student  

where sno in  

  ( select distinct a.sno  

  from  

    (select \* from sc where cno='c002'  

    )a,  

    (select \* from sc where cno='c001'  

    )b  

  where a.score<b.score  

  )  

select \*  

from student st  

join sc a  

on st.sno=a.sno  

join sc b  

on st.sno   =b.sno  

where a.cno ='c002'  

and b.cno   ='c001'  

and a.score < b.score  

```  

## 9、查询所有课程成绩小于60 分的同学的学号、姓名；  

```sql  

select st.\*,  

  s.score  

from student st  

join sc s  

on st.sno= s.sno  

join course co  

on s.cno     = co.cno  

where s.score<60;  

select st.\*,  

  s.score  

from student st  

join sc s  

on st.sno=s.sno  

join course c  

on s.cno      =c.cno  

where s.score <60  

```  

## 10、查询没有学全所有课的同学的学号、姓名；  

```sql  

select \*  

from student st  

join  

  (select s.sno,  

    count(s.cno)cs  

  from sc s  

  group by s.sno  

  having count(s.cno)<  

    (select count(cno)from course  

    )  

  ) s1  

on st.sno=s1.sno;  

```  

## 11、查询至少有一门课与学号为“s001”的同学所学相同的同学的学号和姓名；  

```sql  

select \*  

from student  

where sno in  

  (select sno  

  from  

    (select \* from sc  

    )a,  

    (select cno from sc where sc.sno='s001'  

    )b  

  where a.cno=b.cno  

  and a.sno! ='s001'  

  );  

```  

## 12、查询至少学过学号为“s001”同学所有一门课的其他同学学号和姓名；  

```sql  

```  

## 13、把“SC”表中“谌燕”老师教的课的成绩都更改为此课程的平均成绩；  

### -1.  

```sql  

update sc  

set score=  

  (select a.cno,  

    avg(score)  

  from sc a  

  join course b  

  on a.cno=b.cno  

  join teacher c  

  on c.tno =b.tno  

  and tname='谌燕'  

  group by a.cno  

  )  

where cno in  

  (select a.cno  

  from sc a  

  join course b  

  on a.cno=b.cno  

  join teacher c  

  on c.tno =b.tno  

  and tname='谌燕'  

  );  

```  

### -2.  

```sql  

update s  

set s.score = tt.avgs  

from sc s,  

  (select cno,  

    avg(score) avgs  

  from sc  

  where cno in  

    ( select cno from teacher t,course c where t.tno=c.tno and t.tname='谌燕'  

    )  

  group by cno  

  ) tt  

where tt.cno = s.cno;  

```  

## 14、查询和“s001”号的同学学习的课程完全相同的其他同学学号和姓名；  

```sql  

```  

## 15、删除学习“谌燕”老师课的SC 表记录；  

```sql  

delete sc  

where cno in  

  (select cno from teacher t, course c where t.tname='谌燕'and c.tno= t.tno  

  );  

```  

## 16、向SC 表中插入一些记录，这些记录要求符合以下条件：没有上过编号“c002”课程的同学学号、“c002”号课的平均成绩；  

```sql  

insert  

into sc  

  (  

    sno,  

    cno,  

    score  

  )  

select distinct st.sno,  

  s.cno,  

  (select avg(score) from sc where cno='c002'  

  )  

from sc s,  

  student st  

where st.sno in  

  (select distinct sno from sc where cno!='c002'  

  );  

```  

## 17、查询各科成绩最高和最低的分：以如下形式显示：课程ID，最高分，最低分  

```sql  

select cno 课程ID ,  

  max(score)最高分,  

  min(score)最低分  

from sc  

group by cno;  

```  

## 18、按各科平均成绩从低到高和及格率的百分数从高到低顺序  

```sql  

select cno,  

  avg(score),  

  SUM(  

  case  

    when score>60  

    THEN 1  

    else 0  

  end)/count(\*)  

from sc  

group by cno  

```  

## 19、查询不同老师所教不同课程平均分从高到低显示  

```sql  

select t.tno,  

  t.tname,  

  c.cno,  

  avg(s.score)  

from sc s,  

  teacher t,  

  course c  

where c.tno= t.tno  

and c.cno  = s.cno  

group by c.cno;  

```  

## 20、统计列印各科成绩,各分数段人数:课程ID,课程名称,[100-85],[85-70],[70-60],[ <60]  

```sql  

select sc.cno,  

  c.cname,  

  sum(  

  case  

    when score between 85 and 100  

    THEN 1  

    else 0  

  end ) "[100-85]",  

  sum(  

  case  

    when score between 70 and 85  

    THEN 1  

    else 0  

  end )"[85-70]",  

  sum(  

  case  

    when score between 70 and 60  

    THEN 1  

    else 0  

  end ) "[70-60]",  

  sum(  

  case  

    when score<60  

    THEN 1  

    else 0  

  end )"[<60]"  

FROM sc,  

  course c  

where sc.cno = c.cno  

group by sc.cno,  

  c.cname;  

```  

## 21、查询各科成绩前三名的记录:(不考虑成绩并列情况)  

```sql  

select \*  

from  

  (select sno,  

    cno,  

    score,  

    row\_number()over (partition BY cno order by score DESC)rn  

  from sc  

  )  

where rn<4;  

```  

## 22、查询每门课程被选修的学生数  

```sql  

select cno, count(sno)from sc group by cno;  

```  

## 23、查询出只选修了一门课程的全部学生的学号和姓名  

```sql  

select s1.sno,  

  s1.sname  

from student s1  

join  

  (select sno,count(cno) from sc group by sno HAVING count(cno)=1  

  )s2  

on s1.sno= s2.sno;  

```  

## 24、查询男生、女生人数  

```sql  

select ssex, count(ssex) from student group by ssex;  

```  

## 25、查询姓“张”的学生名单  

```sql  

select \* from student where sname like '张%';  

```  

## 26、查询同名同姓学生名单，并统计同名人数  

```sql  

select sname,  

  count(\*)  

from student  

group by sname  

having count(\*)>1;  

```  

## 27、1990 年出生的学生名单(注：Student 表中Sage 列的类型是number)  

```sql  

select \*  

from student  

where to\_char(sysdate,'yyyy')- sage=1990;  

```  

## 28、查询每门课程的平均成绩，结果按平均成绩升序排列，平均成绩相同时，按课程号降序排列  

```sql  

select cno,  

  avg(score)  

from sc  

group by cno  

order BY avg(score),  

  cno desc;  

```  

## 29、查询平均成绩大于85 的所有学生的学号、姓名和平均成绩  

```sql  

select st.sno,  

  st.sname,  

  ss.\*  

from student st,  

  (select sno,avg(score)ags from sc group by sno having avg(score)>70  

  )ss  

where st.sno=ss.sno  

```  

## 30、查询课程名称为“SSH”，且分数低于60 的学生姓名和分数  

```sql  

select distinct st.sname,  

  sc.score  

from student st  

join course c  

on c.cname='SSH'  

join sc  

ON sc.score<80  

and sc.sno = st.sno  

and c.cno  = sc.cno;  

```  

## 31、查询所有学生的选课情况；  

```sql  

select st.sno,  

  st.sname,  

  c.cname  

from student st,  

  sc,  

  course c  

where sc.sno=st.sno  

and sc.cno  =c.cno;  

```  

## 32、查询任何一门课程成绩在70 分以上的姓名、课程名称和分数；  

```sql  

select st.sname,  

  c.cname,  

  sc.score  

from student st,  

  course c,  

  sc  

where st.sno=sc.sno  

and sc.cno  =c.cno  

and sc.score>70;  

```  

## 33、查询不及格的课程，并按课程号从大到小排列  

```sql  

select c.cno,  

  c.cname,  

  sc.score  

from course c,  

  sc  

where sc.score<60  

and sc.cno    =c.cno;  

```  

## 34、查询课程编号为c001 且课程成绩在80 分以上的学生的学号和姓名；  

```sql  

select st.sno,  

  st.sname  

from student st,  

  sc  

where sc.score>80  

and st.sno    =sc.sno  

and sc.cno    = 'c001';  

## 35、求选了课程的学生人数  

```sql  

select count(DISTINCT sno)from sc;  

```  

## 36、查询选修“谌燕”老师所授课程的学生中，成绩最高的学生姓名及其成绩  

```sql  

select st.sname,  

  sc.score  

from course c,  

  sc,  

  student st,  

  teacher t  

where t.tname='谌燕'  

and t.tno    = c.tno  

and c.cno    = sc.cno  

and st.sno   = sc.sno  

and sc.score =  

  ( select max(score) from sc where sc.cno= c.cno  

  )  

```  

## 37、查询各个课程及相应的选修人数  

```sql  

select cno ,count(sno) from sc group by cno;  

```  

## 38、查询不同课程成绩相同的学生的学号、课程号、学生成绩  

```sql  

select s1.sno,  

  s1.cno,  

  s1.score  

from sc s1,  

  sc s2  

where s1.score=s2.score  

and s1.cno!   = s2.cno;  

```  

## 39、查询每门功课成绩最好的前两名  

```sql  

```  

## 40、统计每门课程的学生选修人数（超过10 人的课程才统计）。要求输出课程号和选修人数，查询结果按人数降序排列，若人数相同，按课程号升序排列  

```sql  

select cno,  

  count(sno)  

from sc  

group by cno  

having count(sno)>10  

order by count(sno)desc,  

  cno ASC;  

```  

## 41、检索至少选修两门课程的学生学号  

```sql  

select sno ,  

  count(cno)  

from sc  

group by sno  

having count(cno)>=2;  

```  

## 42、查询全部学生都选修的课程的课程号和课程名  

```sql  

select DISTINCT c.cname,  

  c.cno  

from course c,  

  sc  

where c.cno=sc.cno;  

```  

## 43、查询没学过“谌燕”老师讲授的任一门课程的学生姓名  

```sql  

select st.sname  

from student st  

where sno not in  

  ( select distinct sno  

  from sc,  

    course c,  

    teacher t  

  where t.tname= '谌燕'  

  and c.tno    =t.tno  

  and sc.cno   = c.cno  

  )  

```  

## 44、查询两门以上不及格课程的同学的学号及其平均成绩  

```sql  

select sno,  

  avg(score)  

FROM sc s  

where sno in  

  ( select sno from sc where sc.score<60 group by sno having count(sno)>1  

  )  

group by sno;  

```  

## 45、检索“c004”课程分数小于60，按分数降序排列的同学学号  

```sql  

select sno,  

  score  

from sc  

where score>60  

and cno    ='c002'  

order by score;  

```  

## 46、删除“s002”同学的“c001”课程的成绩  

```sql  

delete sc where cno='c001' and sno='s002';  

select \* from sc order by sno;  

```
